from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict
import requests

class SpaceXEntity(ABC):
    """Base abstract class for all SpaceX-related entities"""
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self._api_base_url = "https://api.spacexdata.com/v4"

    @abstractmethod
    def fetch_details(self) -> Dict:
        """Abstract method to fetch details from API"""
        pass

    def to_dict(self) -> Dict:
        """Convert entity to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name
        }

class Mission(SpaceXEntity):
    """Class representing a SpaceX mission/launch"""
    def __init__(self, id: str, name: str, date_utc: str, success: bool):
        super().__init__(id, name)
        self.date = datetime.fromisoformat(date_utc.replace('Z', '+00:00'))
        self.success = success
        self.details: Optional[str] = None
        self.links: Dict = {}

    def fetch_details(self) -> Dict:
        """Fetch mission details from API"""
        response = requests.get(f"{self._api_base_url}/launches/{self.id}")
        data = response.json()
        self.details = data.get('details')
        self.links = data.get('links', {})
        return data

class Vehicle(SpaceXEntity):
    """Base class for SpaceX vehicles"""
    def __init__(self, id: str, name: str, type_: str):
        super().__init__(id, name)
        self.type = type_
        self.description: Optional[str] = None
        self.specifications: Dict = {}

    @abstractmethod
    def get_success_rate(self) -> float:
        """Calculate success rate of the vehicle"""
        pass

class Rocket(Vehicle):
    """Class representing a SpaceX rocket"""
    def __init__(self, id: str, name: str):
        super().__init__(id, name, type_="rocket")
        self.stages: int = 0
        self.launches: List[str] = []

    def fetch_details(self) -> Dict:
        """Fetch rocket details from API"""
        response = requests.get(f"{self._api_base_url}/rockets/{self.id}")
        data = response.json()
        self.description = data.get('description')
        self.stages = data.get('stages', 0)
        self.specifications = {
            "height": data.get('height', {}).get('meters'),
            "diameter": data.get('diameter', {}).get('meters'),
            "mass": data.get('mass', {}).get('kg')
        }
        return data

    def get_success_rate(self) -> float:
        """Calculate rocket's success rate"""
        if not self.launches:
            return 0.0
        successful = len([launch for launch in self.launches if launch.success])
        return (successful / len(self.launches)) * 100

class Crew(SpaceXEntity):
    """Class representing SpaceX crew members"""
    def __init__(self, id: str, name: str, agency: str):
        super().__init__(id, name)
        self.agency = agency
        self.missions: List[Mission] = []
        self.status: str = "active"
        self.image: Optional[str] = None
        self.wikipedia: Optional[str] = None
        self.launches: List[str] = []

    def fetch_details(self) -> Dict:
        """Fetch crew member details from API"""
        response = requests.get(f"{self._api_base_url}/crew/{self.id}")
        data = response.json()
        self.status = data.get('status', 'unknown')
        self.image = data.get('image')
        self.wikipedia = data.get('wikipedia')
        self.launches = data.get('launches', [])
        return data

class DataManager:
    """Class to manage data fetching and caching"""
    def __init__(self):
        self.missions: Dict[str, Mission] = {}
        self.rockets: Dict[str, Rocket] = {}
        self.crew: Dict[str, Crew] = {}
        self._api_base_url = "https://api.spacexdata.com/v4"

    def fetch_latest_mission(self) -> Mission:
        """Fetch the latest SpaceX mission"""
        response = requests.get(f"{self._api_base_url}/launches/latest")
        data = response.json()
        
        mission = Mission(
            id=data['id'],
            name=data['name'],
            date_utc=data['date_utc'],
            success=data['success']
        )
        self.missions[mission.id] = mission
        return mission

    def fetch_all_missions(self) -> List[Mission]:
        """Fetch all SpaceX missions"""
        response = requests.get(f"{self._api_base_url}/launches")
        missions = []
        for data in response.json():
            mission = Mission(
                id=data['id'],
                name=data['name'],
                date_utc=data['date_utc'],
                success=data['success']
            )
            self.missions[mission.id] = mission
            missions.append(mission)
        return missions

    def fetch_all_crew(self) -> List[Crew]:
        """Fetch all SpaceX crew members"""
        try:
            response = requests.get(f"{self._api_base_url}/crew")
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Try to parse the JSON response
            data = response.json()
            
            # If we get here, we have valid JSON data
            crew_members = []
            for crew_data in data:
                crew_member = Crew(
                    id=crew_data['id'],
                    name=crew_data['name'],
                    agency=crew_data['agency']
                )
                # Store additional details
                crew_member.image = crew_data.get('image')
                crew_member.wikipedia = crew_data.get('wikipedia')
                crew_member.status = crew_data.get('status', 'unknown')
                crew_member.launches = crew_data.get('launches', [])
                
                self.crew[crew_member.id] = crew_member
                crew_members.append(crew_member)
            return crew_members
            
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {str(e)}")
            print(f"URL attempted: {self._api_base_url}/crew")
            if hasattr(e, 'response'):
                print(f"Status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            raise Exception(f"Failed to fetch crew data: {str(e)}")
            
        except ValueError as e:
            print(f"JSON Parsing Error: {str(e)}")
            print(f"Response content: {response.text}")
            raise Exception("Failed to parse crew data from API")
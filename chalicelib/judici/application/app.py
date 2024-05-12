from chalice import Chalice
from pydantic import BaseModel
from judici.application.settings import settings
    
    
    
class AppChalice(BaseModel):

    @classmethod
    def setings(cls):
        return settings
    
    @classmethod
    def create_app(cls):
        return Chalice(app_name=settings.app_name)
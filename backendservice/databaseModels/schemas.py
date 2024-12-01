from pydantic import BaseModel

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class Login(BaseModel):
    username: str
    password: str

class OrganizationCreate(BaseModel):
    name: str
    invite_code: str

class UserInOrganization(BaseModel):
    username: str
    role: str  # Role in the organization (admin, developer, viewer)

class OrganizationResponse(BaseModel):
    id: int
    name: str
    invite_code: str

class ClusterCreate(BaseModel):
    name: str
    ram: int
    cpu: int
    gpu: int

class ClusterResponse(BaseModel):
    id: int
    name: str
    ram: int
    cpu: int
    gpu: int
    allocated_ram: int
    allocated_cpu: int
    allocated_gpu: int

    class Config:
        orm_mode = True

class JoinOrganizationRequest(BaseModel):
    invite_code: str

class ResourceAllocationRequest(BaseModel):
    ram: int
    cpu: int
    gpu: int

class DeploymentCreate(BaseModel):
    image_path: str
    ram: int
    cpu: int
    gpu: int
    priority: int


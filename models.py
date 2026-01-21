from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FaceDescriptor(BaseModel):
    """Single face descriptor array"""
    data: List[float] = Field(..., description="128-dimensional face descriptor array")

class LabeledFaceDescriptor(BaseModel):
    """Face descriptor with label"""
    label: str = Field(..., description="Student ID or person identifier")
    descriptors: List[List[float]] = Field(..., description="List of face descriptor arrays")
    image_data: Optional[str] = None  # Add this field

class FaceRegistrationRequest(BaseModel):
    """Request model for face registration"""
    data: List[LabeledFaceDescriptor] = Field(..., description="List of labeled face descriptors")

class FaceRegistrationResponse(BaseModel):
    """Response model for face registration"""
    success: bool
    message: str
    registered_count: int
    student_id: Optional[str] = None

class PersonRecord(BaseModel):
    """Database model for person record"""
    student_id: str = Field(..., description="Unique student identifier")
    descriptors: List[List[float]] = Field(..., description="Face descriptor arrays")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

class GetAllFacesResponse(BaseModel):
    """Response model for getting all registered faces"""
    success: bool
    count: int
    data: List[dict]

class DeleteFaceRequest(BaseModel):
    """Request model for deleting faces"""
    student_ids: List[str] = Field(..., description="List of Student IDs to delete")

class DeleteFaceResponse(BaseModel):
    """Response model for face deletion"""
    success: bool
    message: str
    deleted_count: int = 0  # Changed from deleted_student_id

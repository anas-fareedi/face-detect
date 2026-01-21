from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from models import (
    FaceRegistrationRequest,
    FaceRegistrationResponse,
    GetAllFacesResponse,
    DeleteFaceRequest,
    DeleteFaceResponse,
)

router = APIRouter()

def get_database(request: Request):
    """Dependency to get database instance"""
    return request.app.state.db

@router.post("/face/register", response_model=FaceRegistrationResponse)
async def register_face(request: FaceRegistrationRequest, db=Depends(get_database)):
    """
    Register or update face descriptors for a person
    
    - **data**: List of labeled face descriptors with student IDs
    """
    try:
        collection = db["face_descriptors"]
        registered_count = 0
        last_student_id = None
        
        for item in request.data:
            student_id = item.label
            descriptors = item.descriptors
            image_data = getattr(item, "image_data", None)
            
            # DEBUG: Check if image_data is received
            print(f"Registering {student_id}")
            print(f"Image data exists: {image_data is not None}")
            if image_data:
                print(f"Image data length: {len(image_data)}")
            
            existing = await collection.find_one({"student_id": student_id})
            
            doc = {
                "student_id": student_id,
                "descriptors": descriptors,
                "image_data": image_data,  # Make sure this is included
                "updated_at": datetime.utcnow(),
                "is_active": True,
            }
            
            if existing:
                await collection.update_one({"student_id": student_id}, {"$set": doc})
            else:
                doc["created_at"] = datetime.utcnow()
                await collection.insert_one(doc)
            
            registered_count += 1
            last_student_id = student_id
        
        return FaceRegistrationResponse(
            success=True,
            message=f"Registered/updated {registered_count}",
            registered_count=registered_count,
            student_id=last_student_id
        )
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Error registering: {str(e)}")

@router.get("/face/all", response_model=GetAllFacesResponse)
async def get_all_faces(db=Depends(get_database)):
    """
    Return all registered face descriptors.
    """
    try:
        collection = db["face_descriptors"]
        docs = await collection.find({"is_active": {"$ne": False}}).to_list(10000)

        data = [
            {
                "id": str(doc.get("_id", "")),
                "label": doc.get("student_id", ""),
                "descriptors": doc.get("descriptors", []),
                "image_data": doc.get("image_data"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
            }
            for doc in docs
        ]

        return {
            "success": True,
            "message": "Faces fetched",
            "count": len(data),      # add count to satisfy the response model
            "data": data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching faces: {e}")


@router.get("/face/{student_id}")
async def get_face_by_id(student_id: str, db = Depends(get_database)):
    """
    Get face descriptor for a specific student
    
    - **student_id**: The student ID to search for
    """
    try:
        collection = db["face_descriptors"]
        person = await collection.find_one({"student_id": student_id, "is_active": True})
        
        if not person:
            raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found")
        
        return {
            "success": True,
            "data": {
                "label": person["student_id"],
                "descriptors": person["descriptors"],
                "created_at": person.get("created_at"),
                "updated_at": person.get("updated_at")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching face: {str(e)}")

@router.delete("/face/delete", response_model=DeleteFaceResponse)
async def delete_face(request: DeleteFaceRequest, db=Depends(get_database)):
    """
    Delete faces by student_ids.
    """
    try:
        collection = db["face_descriptors"]
        deleted = 0
        
        for student_id in request.student_ids:
            result = await collection.delete_one({"student_id": student_id})
            deleted += result.deleted_count
            print(f"Deleted {student_id}: {result.deleted_count} records")
        
        return DeleteFaceResponse(
            success=True,
            message=f"Deleted {deleted} face(s)",
            deleted_count=deleted
        )
    except Exception as e:
        print(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting face: {str(e)}")
    
@router.delete("/face/permanent/{student_id}")
async def permanent_delete_face(student_id: str, db = Depends(get_database)):
    """
    Permanently delete a face record from database
    
    - **student_id**: The student ID to permanently delete
    """
    try:
        collection = db["face_descriptors"]
        
        result = await collection.delete_one({"student_id": student_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Student ID '{student_id}' not found")
        
        return {
            "success": True,
            "message": f"Permanently deleted face for student ID: {student_id}",
            "deleted_student_id": student_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error permanently deleting face: {str(e)}")

@router.get("/face/count")
async def get_face_count(db = Depends(get_database)):
    """
    Get total count of registered faces
    """
    try:
        collection = db["face_descriptors"]
        count = await collection.count_documents({"is_active": True})
        
        return {
            "success": True,
            "count": count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting faces: {str(e)}")

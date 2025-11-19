from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from app.services.pathfinding import PathfindingService
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.core.config import settings

router = APIRouter(prefix="/api/pathfinding", tags=["pathfinding"])


class PixelCoordinate(BaseModel):
    """Model cho tọa độ pixel từ frontend"""
    x: float
    y: float


class PathRequest(BaseModel):
    """Model cho request tìm đường"""
    start_x: float
    start_y: float
    end_x: float
    end_y: float


class CoordinatePoint(BaseModel):
    """Model cho điểm tọa độ"""
    x: float
    y: float


class PathResponse(BaseModel):
    """Model cho response đường đi"""
    path: List[str]
    coordinates: List[CoordinatePoint]
    total_distance: float


class NodesResponse(BaseModel):
    """Model cho response danh sách nodes"""
    name: str
    x: float
    y: float


@router.get("/nodes", response_model=List[NodesResponse])
async def get_all_nodes(request: Request):
    """
    Lấy danh sách tất cả nodes (từ cache của PathfindingService để tránh query DB mỗi lần)
    """
    try:
        pathfinding: PathfindingService = request.app.state.pathfinder
        if pathfinding is None:
            raise HTTPException(status_code=500, detail="Pathfinder service not initialized")

        result = []
        for name, node in pathfinding.nodes.items():
            result.append({"name": name, "x": node.x, "y": node.y})
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-nearest-node", response_model=Optional[str])
async def find_nearest_node(
    coord: PixelCoordinate,
    request: Request
):
    """
    Tìm node gần nhất với tọa độ pixel được click (dùng cached nodes)
    """
    try:
        pathfinding: PathfindingService = request.app.state.pathfinder
        if pathfinding is None:
            raise HTTPException(status_code=500, detail="Pathfinder service not initialized")

        nearest = pathfinding.find_nearest_node(coord.x, coord.y, max_distance=150)
        return nearest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-path", response_model=Optional[PathResponse])
async def find_path(
    request_body: PathRequest,
    request: Request
):
    """
    Tìm đường đi (sử dụng instance PathfindingService đã được khởi tạo một lần)
    """
    try:
        pathfinding: PathfindingService = request.app.state.pathfinder
        if pathfinding is None:
            raise HTTPException(status_code=500, detail="Pathfinder service not initialized")

        # Tìm 2 node gần nhất từ cache
        start_node = pathfinding.find_nearest_node(request_body.start_x, request_body.start_y)
        end_node = pathfinding.find_nearest_node(request_body.end_x, request_body.end_y)

        if not start_node or not end_node:
            raise HTTPException(status_code=404, detail="Không tìm thấy node gần vị trí được click")

        result = pathfinding.get_path_with_coordinates(start_node, end_node)

        if result is None:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy đường đi từ {start_node} đến {end_node}")

        return PathResponse(
            path=result['path'],
            coordinates=[CoordinatePoint(x=coord[0], y=coord[1]) for coord in result['coordinates']],
            total_distance=result['total_distance']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
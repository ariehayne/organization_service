import sys
import json

from fastapi import APIRouter, Request
from Organization import get_organization
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

sys.path.append("/app")

router = APIRouter()

tree = get_organization()

@router.get("/sort_employees_by")
def filter_employees(by_column: str, ascending = False):
    return tree.get_sorted_employees(by_column, ascending)


@router.get("/get_mailbox_by_size")
def filter_employees(size: int):
    return tree.filter_employees_by_param_range('size', size, size)


@router.get("/get_mailbox_by_size_range")
def filter_employees(min_size: int, max_size : int):
    return tree.filter_employees_by_param_range('size', min_size, max_size)


@router.get("/get_mailbox_by_depth")
def filter_employees(depth: int):
    return tree.filter_employees_by_param_range('depth', depth, depth)


@router.get("/get_mailbox_by_depth_range")
def filter_employees(min_depth: int, max_depth: int):
    return tree.filter_employees_by_param_range('depth', min_depth, max_depth)


@router.get("/filter_mailbox")
def filter_employees(request: Request):
    filters = dict(request.query_params)  # Extract query parameters as a dictionary
    return tree.filter_employees_by_params(filters)


@router.get("/filter_mailbox_partial")
def filter_employees(request: Request):
    filters = dict(request.query_params)  # Extract query parameters as a dictionary
    return tree.filter_employees_by_params_partial(filters)


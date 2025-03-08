import copy

import pandas as pd

from fastapi import APIRouter
from typing import Dict, Optional
from fastapi.responses import JSONResponse


class Employee:
    def __init__(self, employee_row, manager):
        self.user_full_name = employee_row.user_full_name
        self.mailbox_identifier = employee_row.mailbox_identifier
        self.department_id = employee_row.department_id
        self.department_name = employee_row.department_name
        self.job_title = employee_row.job_title
        self.manager = manager
        self.subordinates = []
        self.sub_organization_size = 1

        if manager:
            manager.add_subordinate(self)

    def add_subordinate(self, employee: 'Employee'):
        self.subordinates.append(employee)
        self.update_size()

    def remove_subordinate(self, employee: 'Employee'):
        self.subordinates = [sub for sub in self.subordinates if sub != employee]
        self.update_size()

    def update_size(self):
        self.sub_organization_size = 1 + sum(sub.sub_organization_size for sub in self.subordinates)
        if self.manager:
            self.manager.update_size()

    def get_depth(self):
        depth = 0
        current = self
        while current.manager:
            depth += 1
            current = current.manager
        return depth

    def check_param_in_range(self, param, range_size):
        if param == 'size':
            return self.sub_organization_size in range_size
        elif param == 'depth':
            return self.get_depth in range_size
        else:
            return False


class Organization:
    def __init__(self):
        self.employees = {}

    def add_employee(self, employ_row):
        if employ_row.mailbox_identifier in self.employees:
            return JSONResponse(content={"error": "Employee already exists"}, status_code=400)

        manager = self.employees.get(employ_row.manager_mailbox_identifier)
        if not pd.isna(employ_row.manager_mailbox_identifier) and not manager:
            return JSONResponse(content={"error": "Manager not found"}, status_code=404)

        self.employees[employ_row.mailbox_identifier] = Employee(employ_row, manager)
        return JSONResponse(content={"message": "Employee added successfully"})

    def remove_employee(self, mailbox_identifier: str):
        if mailbox_identifier not in self.employees:
            return JSONResponse(content={"error": "Employee not found"}, status_code=404)

        employee = self.employees[mailbox_identifier]
        if employee.manager:
            employee.manager.remove_subordinate(employee)

        del self.employees[mailbox_identifier]
        return JSONResponse(content={"message": "Employee removed successfully"})

    def get_hierarchy(self):
        return [{"name": emp.user_full_name, "size": emp.sub_organization_size, "manager": emp.manager.user_full_name if emp.manager else None} for emp in
                self.employees.values()]

    def validate_response(self, res):
        if not res:
            return JSONResponse(content={"error": "No matching records found"}, status_code=404)
        return JSONResponse(content=[{"user_full_name": emp.user_full_name,
                                      "mailbox_identifier": emp.mailbox_identifier,
                                      "job_title": emp.job_title,
                                      "department": emp.department_name,
                                      "sub_organization_size": emp.sub_organization_size,
                                      "manager_name": emp.manager.user_full_name if emp.manager else None} for emp in res])

    def filter_employees_by_param_range(self, param, min_depth, max_depth):
        filtered = []
        for emp in self.employees.values():
            if emp.check_param_in_range(param, range(min_depth, max_depth+1)):
                filtered.append(emp)
        return self.validate_response(filtered)

    def filter_employees_by_params_partial(self, filters: Dict[str, str]):
        filtered = [
            emp for emp in self.employees.values()
            if all(
                value in getattr(emp, key, None) for key, value in filters.items()
            )
        ]
        return self.validate_response(filtered)

    def filter_employees_by_params(self, filters: Dict[str, str]):
        filtered = [
            emp for emp in self.employees.values()
            if all(
                str(getattr(emp, key, None)) == str(value) if isinstance(getattr(emp, key, None), int) else getattr(emp, key, None) == value
                for key, value in filters.items()
            )
        ]
        return self.validate_response(filtered)

    def get_sorted_employees(self, by_column, ascending=False):
        res = copy.deepcopy(list(self.employees.values()))
        return self.validate_response(sorted(res, key=lambda x: getattr(x, by_column), reverse=not ascending))


def get_organization() -> Organization:
    Mailboxes = pd.read_csv('./data/Mailboxes.csv')
    Departments = pd.read_csv('./data/Departments.csv')
    merged_data = Mailboxes.merge(Departments, on='department_id')

    tree = Organization()
    for index, row in merged_data.iterrows():
        tree.add_employee(row)
    return tree

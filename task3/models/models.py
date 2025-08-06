import random
from collections import deque
from datetime import time, timedelta, timezone, datetime
from zoneinfo import ZoneInfo

from settings import TIME_ZONE


class Node:
    def __init__(self, parent_id, dep_id, head_id=None):
        self.parent_id = parent_id
        self.dep_id = dep_id
        self.head_id = head_id
        self.children = []


class Employee:
    @classmethod
    def get_employee_list(cls, but):
        # raw data
        rawDepartmentList = but.call_api_method("department.get")
        rawUsers = but.call_api_method("user.get", {
            "filter": {
                "!UF_DEPARTMENT": []
            }
        }
                                       )
        if not rawDepartmentList.get('result') or not rawUsers.get('result'):
            return None
        departmentINFOs = {}
        for dep in rawDepartmentList.get('result'):
            departmentINFOs[dep.get('ID')] = {
                'NAME': dep.get('NAME'),
                'PARENT': dep.get('PARENT'),
                'UF_HEAD': dep.get('UF_HEAD')
            }
        users = []
        users_names = {}
        for user in rawUsers.get('result'):
            ID_DEP = user.get('UF_DEPARTMENT')
            for id in ID_DEP:
                users.append({
                    "ID": user.get('ID'),
                    "NAME": user.get('NAME'),
                    "LAST_NAME": user.get('LAST_NAME'),
                    "UF_DEPARTMENT": id,
                    "DEPARTMENT_NAME": departmentINFOs[str(id)].get('NAME')
                })
            users_names[user.get('ID')] = {
                "ID": user.get('ID'),
                "NAME": user.get('NAME'),
                "LAST_NAME": user.get('LAST_NAME'),
            }
        calls_dict = cls.get_calls(but)
        for user in users:
            user_parents = cls.get_parents_one_dep(user, departmentINFOs, users_names)
            user["PARENTS"] = user_parents
            user["CALLS_NUM"] = 0 if not calls_dict.get(user["ID"]) else calls_dict[user["ID"]]
        return users

    @classmethod
    def get_parents_one_dep(cls, user_info, departmentINFOs, names):
        department = user_info.get('UF_DEPARTMENT', [])
        user_parent_users = []
        q = deque()
        q.append(department)
        visited_heads = set()
        visited_deps = set()

        while q:
            department = q.popleft()
            if department in visited_deps:
                continue
            dep_info = departmentINFOs.get(str(department), {})
            head_id = dep_info.get("UF_HEAD")
            parent_id = dep_info.get("PARENT")

            if head_id:
                visited_heads.add(head_id)
                if head_id != user_info.get("ID"):
                    user_parent_users.append(names[head_id])
            if parent_id:
                q.append(parent_id)
        return user_parent_users

    @classmethod
    def get_parents(cls, user_info, departmentINFOs, names):
        departments = user_info.get('UF_DEPARTMENT', [])
        user_parent_users = []
        q = deque(departments)
        visited_heads = set()
        visited_deps = set()

        while q:
            department = q.popleft()
            if department in visited_deps:
                continue
            dep_info = departmentINFOs.get(str(department), {})
            head_id = dep_info.get("UF_HEAD")
            parent_id = dep_info.get("PARENT")

            if head_id:
                visited_heads.add(head_id)
                if head_id != user_info.get("ID"):
                    user_parent_users.append(head_id)
            if parent_id:
                q.append(parent_id)
            parent = []
            visited = set()
            for i in range(len(user_parent_users)):
                j = user_parent_users[len(user_parent_users) - i - 1]
                if j in visited: continue
                parent.append(names.get(str(j)))
                visited.add(j)
        return reversed(parent)

    @classmethod
    def get_parents(cls, user_info, departmentINFOs, names):
        departments = user_info.get('UF_DEPARTMENT', [])
        user_parent_users = []
        q = deque(departments)
        visited_heads = set()
        visited_deps = set()

        while q:
            department = q.popleft()
            if department in visited_deps:
                continue
            dep_info = departmentINFOs.get(str(department), {})
            head_id = dep_info.get("UF_HEAD")
            parent_id = dep_info.get("PARENT")

            if head_id:
                visited_heads.add(head_id)
                if head_id != user_info.get("ID"):
                    user_parent_users.append(head_id)
            if parent_id:
                q.append(parent_id)
            parent = []
            visited = set()
            for i in range(len(user_parent_users)):
                j = user_parent_users[len(user_parent_users) - i - 1]
                if j in visited: continue
                parent.append(names.get(str(j)))
                visited.add(j)
        return reversed(parent)

    @classmethod
    def get_calls(cls, but):
        current_time = datetime.now(ZoneInfo(TIME_ZONE))
        calls = but.call_api_method('voximplant.statistic.get',
                                    {
                                        "FILTER": {
                                            ">CALL_DURATION": 60,
                                            "CALL_TYPE": 1
                                        },
                                    })
        calls_dict = {}
        for call in calls.get('result'):
            if (current_time - datetime.fromisoformat(call["CALL_START_DATE"])) < timedelta(hours=24):
                user_id = call["PORTAL_USER_ID"]
                if user_id not in calls_dict:
                    calls_dict[user_id] = 0
                calls_dict[user_id] += 1
        return calls_dict

    @classmethod
    def debug_generate_calls(cls, but, number=10, end_time=datetime.now()):
        rawUsers = but.call_api_method("user.get", {
            "filter": {
                "!UF_DEPARTMENT": []
            }
        }
                                       )
        if not rawUsers.get('result'):
            return None
        user_ids = [user['ID'] for user in rawUsers['result']]
        rand_ids = random.choices(user_ids, k=number)
        generated_calls_info = []
        for id in rand_ids:
            generated_calls_info.append(cls.debug_make_call(but, id, end_time=end_time))
        return generated_calls_info

    @classmethod
    def debug_make_call(cls, but, id, type=None, start_time=None, end_time=None, interval_seconds=61):
        if not type:
            type = random.randint(1, 3)
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(seconds=interval_seconds)

        call = but.call_api_method('telephony.externalcall.register',
                                   {
                                       "USER_ID": id,
                                       "PHONE_NUMBER": "8905634534",
                                       "CALL_START_DATE": str(start_time),
                                       "TYPE": type,
                                   }
                                   )
        if not call.get('result'):
            return None
        but.call_api_method('telephony.externalcall.finish',
                            {
                                "CALL_ID": call['result']["CALL_ID"],
                                "USER_ID": id,
                                "DURATION": interval_seconds,
                            }
                            )
        return {
            "CALL_ID": call['result']["CALL_ID"],
            "USER_ID": id,
            "INTERVAL_SECONDS": interval_seconds,
            "START_TIME": start_time,
            "END_TIME": end_time,
            "TYPE": type,
        }

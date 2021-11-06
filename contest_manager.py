from discord.ext import commands

from micro_db import MicroDB
from dmoj_client import DmojClient


CONTEST_DICT_TEMPLATE = {
    "contest_name" : {
        "active": False,
        "registrationRequired": False,
        "EndDate": 0,
        "problems": [],
        "users": [],
    }
}

'''
data to save
    - save user -> dmoj id
    - save contest -> discord user:dmoj id, problems_list
commands
    - check user solved problem
    - create contest
        - contest name, problems
    - get contest result
        - save user results -> csv

    - start contest (allow previous submission = True [default])
    - end contest
        - run get contest

contestDB:
- name, active:True/False, registrationRequierd: deafult=False, EndDate: 0/Date, [problem_ids], [users: id, problems],
- !create_contest true false date link1 link2 link3
'''
class ContestManager(commands.Cog):
    def __init__(self, client, dmoj_client : DmojClient):
        self.client = client
        self._dmoj_client = dmoj_client

        self._users_db = MicroDB("users")
        self._contests_db = MicroDB("contests")

    @commands.command()
    async def create_contest(self, ctx, contest_name, active, registrationRequired, endDate, force, *problem_links):
        force = True if force==True or str(force).lower() == 'force' else False
        active = True if active==True or str(active).lower() == 'active' else False
        registrationRequired = True if registrationRequired==True or str(registrationRequired).lower() == 'required' else False

        if not force and contest_name in self._contests_db.get_all():
            await ctx.send(f"A contest with name: {contest_name} already exists. Use force=true to overwrite.")
            return
        if len(problem_links) == 0:
            await ctx.send("A list of problem(s) is required to create a contest")
            return

        ret = f"Creating contest: {contest_name} with problems:\n"
        problem_ids = []
        for i, problem_url in enumerate(problem_links):
            problem_id = self._get_problem_id_from_url(problem_url)
            problem = await self._dmoj_client.get_problem(problem_id)
            if problem is None:
                await ctx.send(f"Failed to create contest, could not resolve {problem_url}")
                return

            problem_ids.append(problem_id)
            name = problem["name"]
            points = problem["points"]
            ret = ret + f"{i+1}: problem_id= {problem_id}, name={name}, points={points}\n"

        contest_dict = {
            "active": active,
            "registrationRequired": registrationRequired,
            "endDate": endDate,
            "problems": problem_ids,
        }
        self._contests_db.set(contest_name, contest_dict)
        await ctx.send(ret)

    @commands.command()
    async def get_contest(self, ctx, contest_name):
        contest_dict = self._contests_db.get_all()
        if not contest_name in contest_dict:
            await ctx.send("Contest entry not found")
            return
        await ctx.send(f"Contest found with entry: {contest_dict[contest_name]}")

    @commands.command()
    async def user_submission(self, ctx, discord_user, problem_id):
        user_id = self._users_db.get_all().get(discord_user, None)
        if user_id is None:
            await ctx.send(f"Discord user {discord_user} does not have a linked dmoj account")
            return
        problem_id = self._get_problem_id_from_url(problem_id)

        accepted, wrong_submissions = await self._dmoj_client.get_user_submissions(user_id, problem_id)
        if accepted is None:
            await ctx.send(f"Dmoj query failed, user_id: {user_id}, problem_id: {problem_id}")
        elif accepted:
            await ctx.send(f"Accepted solution found after {wrong_submissions} non-AC submissions")
        else:
            if wrong_submissions == 0:
                await ctx.send(f"No submissions found")
            else:
                await ctx.send(f"Found {wrong_submissions} non-AC submissions")

    def _get_problem_id_from_url(self, str):
        i = str.rfind("/")
        ret = str[i+1:] if i + 1 < len(str) and i != -1 else str
        return  ret


CONTEST_DICT_TEMPLATE = {
    "contest_name" : {
        "active": False,
        "registrationRequired": False,
        "EndDate": 0,
        "problems": [],
        "users": [],
    }
}

   


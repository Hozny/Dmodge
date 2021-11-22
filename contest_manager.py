from discord.ext import commands
import json
import datetime

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

class ContestManager(commands.Cog):
    def __init__(self, client, dmoj_client : DmojClient):
        self.client = client
        self._dmoj_client = dmoj_client

        self._users_db = MicroDB("users")
        self._contests_db = MicroDB("contests")

    '''
    @commands.command()
    async def force_add(self, ctx):
        self._users_db.set("Sardor", "donkogronko")

    @commands.command()
    async def print_db(self, ctx):
        await ctx.send(json.dumps(self._contests_db.get_all(), indent=4))
    '''
    
    @commands.command()
    async def create_weekly(self, ctx, week_number, *problem_links):
        contest_name = f"Weekly Problem Set #{week_number}"
        end_date = datetime.datetime.now() + datetime.timedelta(days=7)
        await self._create_contest(ctx, contest_name, True, False, end_date, False, *problem_links)

    @commands.command()
    async def end_weekly(self, ctx, week_number):
        await self.end_contest(ctx, f"Weekly Problem Set #{week_number}")

    @commands.command()
    async def end_contest(self, ctx, contest_name):
        if not contest_name in self._contests_db.get_all():
            await ctx.send("There is no contest with this name")
            return
        
        contest_dict = self._contests_db.get(contest_name)
        users_dict =  self._users_db.get_all()
        endDate = contest_dict["endDate"]
        
        def check(message):
            return message.author.id == ctx.author.id and \
                message.channel == ctx.channel

        if contest_dict["active"] == False:
            await ctx.send("This contest is already over.")
            return

        if datetime.datetime.now() < endDate:
            date_string = endDate.strftime("%B %d, %Y")
            await ctx.send(f"This contest is set to end on {date_string}. Are you sure you want to end the contest anyway?")
            message = await self.client.wait_for("message", check=check)
            if not message.content.lower() in ["y", "yes"]:
                await ctx.send("Okay, aborted.")
                return
        
        contest_dict["active"] = False
        contest_dict["completion"], contest_dict["ranking"] = await self._contest_rankings(contest_name)
        self._contests_db.set(contest_name, contest_dict)

        await ctx.send(json.dumps(contest_dict["completion"], indent=4))
        await ctx.send(contest_dict["ranking"])

    async def _contest_rankings(self, contest_name):
        problems = self._contests_db.get(contest_name)["problems"]
        users_dict = self._users_db.get_all()

        completion = {}
        ranking = []
        for problem in problems: completion[problem] = {}
        for user in users_dict:
            user_dmoj = self._users_db.get(user)
            status = [0,0]
            for problem in problems:
                submission = await self._dmoj_client.get_user_submissions(user_dmoj, problem)
                completion[problem][user] = submission
                status[0] += submission[0]
                status[1] += submission[1]    
            ranking.append((user,status))   
        ranking.sort(key = lambda c: c[1], reverse=True)   
        
        return completion, ranking

    @commands.command()
    async def _create_contest(self, ctx, contest_name, active, registrationRequired, endDate, force, *problem_links):
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
        print(problem_links)
        for i, problem_url in enumerate(problem_links):
            print(problem_url)
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

    #also defined in Dmodge.py for use in user_submission() -- fix that
    def _get_problem_id_from_url(self, str):
        i = str.rfind("/")
        ret = str[i+1:] if i + 1 < len(str) and i != -1 else str
        return ret

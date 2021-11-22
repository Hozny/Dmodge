from discord.ext import commands

from micro_db import MicroDB


class Dmodge(commands.Cog):
    """
    Handles Dmoj related administrative tasks 
        (linking users, searching, etc...)
    """
    def __init__(self, client, dmoj_client):
        self.client = client
        self._dmoj_client = dmoj_client

        self._users_db = MicroDB("users")
    
    @commands.command()
    async def search_problems(self, ctx, query):
        problems = await self._dmoj_client.search_problems(query)

        num_problems = 4
        resp = f"The top {num_problems} problems matching are:\n"
        for i, problem in enumerate(problems):
            if i >= num_problems: break

            name = problem["name"]
            code = problem["code"]
            problem_str = f"Name: {name} - problem_code: {code}\n"
            resp = resp + problem_str

        await ctx.send(resp)

    @commands.command()
    async def link_dmoj_account(self, ctx, user_id):
        if not await self._dmoj_client.is_user_exist(user_id):
            await ctx.send(f"Could not find DMOJ user matching name: {user_id}")
            return

        author = ctx.author.display_name
        authorID = str(ctx.author.id)
        user_data = self._users_db.get_all()
        if user_data.get(authorID) == user_id:
            await ctx.send(f"You're already linked to this account")
            return
        if user_id in user_data.values():
            await ctx.send(f"Account already linked to someone; ask them to unlink or ask for help")
            return

        self._users_db.set(authorID, user_id)
        await ctx.send(f"Succesfully linked {user_id} to {author}.")


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
        return ret

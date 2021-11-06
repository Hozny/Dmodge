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
    async def get_user_submissions(self, ctx, user, problem_id = None):
        """
        !get_user_submission user [problem_id]
        """
        print("received command")
        submissions = await self._dmoj_client.get_user_submission(user, problem_id)
        await ctx.send("I truncated response to :" + str(submissions)[:1000])

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

        author = ctx.author.name
        user_data = self._users_db.get_all()
        if user_data.get(author) == user_id:
            await ctx.send(f"You're already linked to this account")
            return
        if user_id in user_data.values():
            await ctx.send(f"Account already linked to someone; ask them to unlink or ask for help")
            return

        self._users_db.set(author, user_id)
        await ctx.send(f"Succesfully linked accounts discord: {author} to dmoj: {user_id}")



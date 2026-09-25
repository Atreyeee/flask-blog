"""
Populates the database with realistic demo content for showing off the blog
(e.g. in an interview). Safe to re-run: it wipes and recreates all tables first.

Usage:
    python seed.py

Demo login (admin / post owner):
    email:    atreyee@example.com
    password: demo1234
"""
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from main import app, db, User, BlogPost, Comment, Like

DEMO_PASSWORD = "demo1234"

USERS = [
    {"name": "Atreyee Das", "email": "atreyee@example.com"},          # id 1 -> admin
    {"name": "Rahul Mehta", "email": "rahul.mehta@example.com"},
    {"name": "Sara Chen", "email": "sara.chen@example.com"},
]

POSTS = [
    {
        "title": "Why Every Data Analyst Should Learn to Write Clean SQL",
        "subtitle": "Queries you can still read six months later",
        "category": "Data Science",
        "img": "https://picsum.photos/seed/sqlclean/900/600",
        "body": """
        <p>The first SQL queries I wrote worked, but I couldn't explain them a week later. Nested subqueries five levels deep, cryptic aliases like <code>t1</code> and <code>t2</code>, no comments anywhere. They ran, but they weren't something I could hand to a teammate.</p>
        <p>What changed things for me was treating a query like a small program: CTEs instead of nested subqueries so each step has a name, consistent formatting so joins are easy to scan, and aliases that describe what a table actually holds rather than <code>a</code>, <code>b</code>, <code>c</code>.</p>
        <p>It sounds like a small habit, but it's the difference between a query you can maintain and one you quietly rewrite from scratch every time it breaks.</p>
        """,
    },
    {
        "title": "5 Lessons From Building My First Full-Stack Flask App",
        "subtitle": "What actually took time versus what I expected to be hard",
        "category": "Web Development",
        "img": "https://picsum.photos/seed/flasklessons/900/600",
        "body": """
        <p>I assumed the database models would be the hard part. They weren't — SQLAlchemy's ORM made relationships feel almost obvious once I understood <code>relationship()</code> and <code>ForeignKey</code>.</p>
        <p>What actually ate my time: authentication edge cases, deciding what belongs in a template versus a route, and realizing that "it works on my machine" doesn't mean it works with a fresh database.</p>
        <p>The biggest lesson was smaller than any of that, though: build the ugly working version first, then make it look good. I kept wanting to polish the UI before the logic was solid, and that always cost me more time in the end.</p>
        """,
    },
    {
        "title": "Surviving Final Year: Balancing College, Projects, and Job Hunting",
        "subtitle": "Notes to myself from the middle of it",
        "category": "Career",
        "img": "https://picsum.photos/seed/finalyear/900/600",
        "body": """
        <p>Final year has a way of stacking three full-time jobs on top of each other: coursework, a portfolio you're still building, and applications that all seem to be due the same week.</p>
        <p>What's worked for me is picking one project to go deep on rather than starting five shallow ones. A single project I can explain in detail — why I made each decision, what I'd do differently — has been worth more in interviews than a long list of half-finished repos.</p>
        <p>The other thing I had to accept: not every week looks productive from the outside. Some weeks are just reading documentation and getting nowhere, and that's still part of the process.</p>
        """,
    },
    {
        "title": "The Pandas Trick That Saved Me Hours of Data Cleaning",
        "subtitle": "Vectorize before you loop",
        "category": "Data Science",
        "img": "https://picsum.photos/seed/pandastrick/900/600",
        "body": """
        <p>My first instinct with messy data was always a <code>for</code> loop over rows. It works, but on a dataset of even a few thousand rows it's painfully slow — and it doesn't scale.</p>
        <p>Switching to vectorized operations — boolean masks, <code>.apply()</code> only as a last resort, <code>.str</code> accessors for text cleanup — cut a cleaning script that used to take minutes down to under a second.</p>
        <p>The mental shift was thinking in terms of whole columns instead of individual records. Once that clicked, a lot of pandas started to make more sense.</p>
        """,
    },
    {
        "title": "Why I Rebuilt My Morning Routine (And What Actually Changed)",
        "subtitle": "Less about discipline, more about removing friction",
        "category": "Personal",
        "img": "https://picsum.photos/seed/morningroutine/900/600",
        "body": """
        <p>I used to think a good morning routine was about willpower. It's mostly about removing the small decisions that eat your first hour — what to wear, what to eat, where your laptop charger is.</p>
        <p>Laying things out the night before turned out to matter more than any productivity app I tried. It's not exciting advice, but it's the one thing that's actually stuck for more than two weeks.</p>
        """,
    },
    {
        "title": "Docker for Beginners: What I Wish I Knew Before My First Container",
        "subtitle": "It's not as mysterious as it looks",
        "category": "Technology",
        "img": "https://picsum.photos/seed/dockerbeginner/900/600",
        "body": """
        <p>For a long time I avoided Docker because it seemed like infrastructure that only "real" engineers needed. Then a project wouldn't run on a teammate's laptop because of a Python version mismatch, and Docker suddenly made sense.</p>
        <p>A container is just a consistent box your code runs in, described by a <code>Dockerfile</code> you can read top to bottom. The learning curve is mostly vocabulary — image, container, volume, layer — not actual difficulty.</p>
        <p>Once I ran my first <code>docker build</code> and <code>docker run</code>, the rest was just iterating on a text file.</p>
        """,
    },
    {
        "title": "Building an HR Analytics Dashboard With Synthetic Data",
        "subtitle": "Why fake data can still teach you real skills",
        "category": "Data Science",
        "img": "https://picsum.photos/seed/hrdashboard/900/600",
        "body": """
        <p>Without access to a real company's HR data, I generated a synthetic dataset of employee records using Python and Faker — names, salaries, departments, hire dates — all fabricated but statistically plausible.</p>
        <p>Building the Tableau dashboard on top of it still forced the real skills: deciding which KPIs matter, choosing chart types that don't mislead, and designing filters that a non-technical stakeholder could actually use.</p>
        <p>The data wasn't real, but the design decisions were, and that's the part that transfers to an actual job.</p>
        """,
    },
    {
        "title": "REST APIs Explained the Way I Wish Someone Had Explained Them to Me",
        "subtitle": "No jargon, just the mental model",
        "category": "Web Development",
        "img": "https://picsum.photos/seed/restapi/900/600",
        "body": """
        <p>A REST API is just a set of URLs your code can ask questions of, using the same verbs a browser already knows: GET to read something, POST to create it, PUT or PATCH to change it, DELETE to remove it.</p>
        <p>What confused me at first was status codes — until I started reading them as a sentence: 200 means "here you go," 404 means "that doesn't exist," 401 means "who are you, exactly."</p>
        <p>Once I stopped treating endpoints as magic and started treating them as predictable, well-named functions, testing them in Postman stopped feeling like guesswork.</p>
        """,
    },
    {
        "title": "Three Productivity Habits That Actually Stuck",
        "subtitle": "Out of the dozen I tried",
        "category": "Productivity",
        "img": "https://picsum.photos/seed/productivityhabits/900/600",
        "body": """
        <p>I've tried more productivity systems than I'd like to admit. Most lasted a week. Three habits made it past the first month.</p>
        <p>First: writing tomorrow's top three tasks the night before, so I'm not deciding what matters at 9am with no coffee in me. Second: closing every tab related to a task the moment it's done, instead of letting fifteen browser tabs quietly guilt-trip me. Third: a single running notes document instead of scattering ideas across five apps.</p>
        <p>None of these are novel. They're just the ones simple enough that I couldn't talk myself out of doing them.</p>
        """,
    },
]

COMMENT_POOL = [
    "This is such a clear explanation, thanks for writing it up!",
    "I ran into the exact same issue last month — wish I'd found this sooner.",
    "Bookmarking this for the next time I forget how this works.",
    "Would love a follow-up post that goes deeper into this.",
    "Really appreciate the honest take here, not just the polished version.",
]


def run():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Users ---
        user_objs = []
        for u in USERS:
            user = User(
                name=u["name"],
                email=u["email"],
                password=generate_password_hash(DEMO_PASSWORD, method="pbkdf2:sha256", salt_length=8),
            )
            db.session.add(user)
            user_objs.append(user)
        db.session.commit()  # so user.id values exist

        admin = user_objs[0]
        others = user_objs[1:]

        # --- Posts ---
        today = date.today()
        post_objs = []
        for i, p in enumerate(POSTS):
            post_date = today - timedelta(days=(len(POSTS) - i) * 6)
            post = BlogPost(
                title=p["title"],
                subtitle=p["subtitle"],
                category=p["category"],
                body=p["body"],
                img_url=p["img"],
                author=admin,
                date=post_date.strftime("%B %d, %Y"),
                views=20 + i * 17 + (i * 7) % 13,
            )
            db.session.add(post)
            post_objs.append(post)
        db.session.commit()

        # --- Comments ---
        for i, post in enumerate(post_objs):
            num_comments = 1 + (i % 3)
            for c in range(num_comments):
                commenter = others[c % len(others)]
                comment = Comment(
                    text=f"<p>{COMMENT_POOL[(i + c) % len(COMMENT_POOL)]}</p>",
                    comment_author=commenter,
                    author_id=commenter.id,
                    post_id=post.id,
                    parent_post=post,
                )
                db.session.add(comment)

        # --- Likes ---
        for i, post in enumerate(post_objs):
            for u_idx, user in enumerate(user_objs):
                if (i + u_idx) % 2 == 0:
                    db.session.add(Like(user_id=user.id, post_id=post.id))

        db.session.commit()
        print(f"Seeded {len(user_objs)} users and {len(post_objs)} posts.")
        print(f"Log in as: {admin.email} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    run()

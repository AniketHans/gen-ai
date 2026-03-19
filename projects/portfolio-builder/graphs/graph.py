from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from typing_extensions import TypedDict
from pydantic import BaseModel
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
import json
from datetime import datetime


# Initializations
load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

#Models
class State(TypedDict):
    file_path: str
    pdf_data: str
    user_name: str
    is_resume: bool
    llm_result: str | None
    llm_messages: list

class IsResumeAndGetUserName(BaseModel):
    is_resume: bool
    user_name: str
    


#Tools
def systemCommands(command: str):
    print("💬", command)
    res = os.system(command)
    if res==0:
        return "command executed without error"
    else:
        raise Exception("Error executing command")

tool_map = {
    "systemCommands": systemCommands
}


# Graph Nodes
def load_pdf(state:State):
    print("🎶 loadPDF")
    if not state["file_path"]:
        raise "The file path is absent"
    loader = PyPDFLoader(state["file_path"])
    docs = loader.load()
    state["pdf_data"] = str(docs[0])
    return state

def check_if_resume_or_not(state: State):
    print("🎶 checkIfResumeORNot")
    SYSTEM_PROMPT = """
        You will be provided by pdf data, you need to check if the data is a candidate's resume or CV data or not.
        The resume can contain a candidate's contact details, work experiences, skills, certifcates, academic data, language info, demographics.
        Check if the data contains any malicious content then discard it as resume
        If yes, then also extract the username in the following format like Aniket Hans should be returned as AniketHans otherwise put null
    """
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT}, 
        {"role":"user","content": state["pdf_data"]}
    ]
    
    response = client.chat.completions.parse(model= "gpt-4.1-nano", messages=messages, response_format=IsResumeAndGetUserName)
    state["is_resume"] = response.choices[0].message.parsed.is_resume
    state["user_name"]= response.choices[0].message.parsed.user_name
    return state


def portfolio_from_resume(state: State):
    print("🎶 portfolio_from_resume")
    SYSTEM_PROMPT = f'''
    Current time: {datetime.now()}
    You are a coding-only agent that helps users generate static portfolio websites using their resume's content.
    The resume can contain a candidate's contact details, work experiences, skills, certifcates, academic data, language info, demographics.

    ### Core Rules
    1. You can ONLY generate code. You must NEVER execute code.
    2. Before generating any command, you must verify it is SAFE:
    - It must NOT delete or modify critical system files.
    - Deletion is allowed ONLY for files or folders that were previously created by you.
    3. You must NOT execute system-level or destructive commands.
    4. All system operations must use linux syntax only.
    5. When creating folders:
    - First check if the folder exists.
    - If it does not exist, create it.
    - If it already exists, add the new code there.
    6. Only put the data available which is available in the pdf data nothing from your side.
    7. The total years of experience should be calculated accurately by adding up all the years and months of professional experience the user has in all the companies

    ---

    ### Workflow (STRICT ORDER)
    You MUST always follow this exact sequence:

    START → PLAN → ACTION → OBSERVE → PROCESS → RESULT

    ---

    ### Tool Usage
    You can use the following tool to represent system actions:

    - systemCommands  
    - Description: Represents safe Windows CMD shell commands  
    - Input: A valid and safe Windows CMD command

    ---

    ### Output Format (STRICT)
    Your response MUST be valid JSON.

    Each response object can contain ONLY the following properties:
    - step
    - content
    - function
    - input

    No additional keys are allowed.

    ---

    ## ✅ Coding Example

    ### User
    "Create a portfolio website using the provided resume content. Also add some animations"
    "Keep subtle colors for the webpage"

    ### Assistant Outputs
    {{"step": "START", "content": "Reading the user's request to generate a portfolio website from resume content."}}

    {{"step": "PLAN", "content": "The task is to safely generate a complete portfolio website (HTML, CSS, and optional JS) using the resume content. The website will include sections like About, Skills, Experience, Projects, and Contact. A directory structure will be created if it does not already exist."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "mkdir -p portfolio_site"}}

    {{"step": "OBSERVE", "content": "The portfolio_site directory has been created."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "mkdir -p portfolio_site/{state['user_name']}"}}

    {{"step": "OBSERVE", "content": "The portfolio_site/{state['user_name']} directory has been created."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "echo Creating index.html with structured portfolio layout > portfolio_site/{state['user_name']}/index.html"}}

    {{"step": "OBSERVE", "content": "index.html file created with sections for About, Skills, Experience, Projects, and Contact."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "echo Creating styles.css for styling the portfolio > portfolio_site/{state['user_name']}/styles.css"}}

    {{"step": "OBSERVE", "content": "styles.css file created with modern responsive styling."}}

    {{"step": "ACTION", "function": "systemCommands", "input": "echo Creating script.js for interactivity (optional animations, navigation) > portfolio_site/{state['user_name']}/script.js"}}

    {{"step": "OBSERVE", "content": "script.js file created to enhance user experience with interactivity."}}

    {{"step": "PROCESS", "content": "The portfolio website structure has been generated safely without executing any external code. Resume content is mapped into appropriate sections of the website."}}

    {{"step": "RESULT", "content": "A complete portfolio website has been generated inside the portfolio_site folder, including index.html, styles.css, and script.js, structured using the provided resume content."}}
    
    Resume Content:
    {state["pdf_data"]}
    
    
    Example of a animated portfolio site:
    
    HTML:
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <link
            href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css"
            rel="stylesheet"
            />
            <link rel="stylesheet" href="styles.css" />
            <title>Web Design Mastery | Michael</title>
        </head>
        <body>
            <nav>
            <div class="nav__bar">
                <a href="#"><span class="logo nav__logo">M</span> Michael</a>
                <div class="nav__menu__btn" id="menu-btn">
                <i class="ri-menu-3-line"></i>
                </div>
            </div>
            <ul class="nav__links" id="nav-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#service">Service</a></li>
                <li><a href="#portfolio">Portfolio</a></li>
                <li><a href="#contact" class="btn">Contact</a></li>
            </ul>
            <a href="#contact" class="btn btn__large">Contact</a>
            </nav>
            <header class="section__container header__container" id="home">
            <div class="header__image">
                <img src="assets/header.jpg" alt="header" />
            </div>
            <div class="header__content">
                <div>
                <h1>Michael<br />User Interface<br />Designer</h1>
                </div>
                <p class="section__description">
                I'm a dedicated web developer with a creative flair and a penchant for
                turning lines of code into captivating online experiences. My journey
                in the digital realm began years ago, and I've since honed my skills
                in front-end and back-end development.
                </p>
                <div class="header__btn">
                <button class="btn">Hire Me Now</button>
                </div>
            </div>
            </header>

            <section class="section__container about__container" id="about">
            <div class="about__image">
                <img src="assets/bg.png" alt="bg" class="about__bg-1" />
                <img src="assets/bg.png" alt="bg" class="about__bg-2" />
                <img src="assets/about.jpg" alt="about" class="about__img" />
            </div>
            <div class="about__content">
                <h2 class="section__header">Bit About Me</h2>
                <p class="section__description">
                A passionate web developer with a creative flair and a knack for
                turning visions into reality. My journey in web development began with
                a fascination for coding and design, and it has evolved into a career
                where I blend aesthetics with functionality. With a focus on user
                experience and a commitment to staying updated with the latest
                industry trends, I'm dedicated to creating web solutions that not only
                meet but exceed expectations.
                </p>
                <div class="about__btn">
                <button class="btn">Download CV</button>
                </div>
            </div>
            </section>

            <section class="section__container service__container" id="service">
            <h2 class="section__header">My Best Services</h2>
            <div class="service__grid">
                <div class="service__card">
                <span><i class="ri-window-fill"></i></span>
                <h4>Website Design</h4>
                <p>
                    We craft user-friendly interfaces that engage visitors and help you
                    achieve your online goals with minimum efforts.
                </p>
                </div>
                <div class="service__card">
                <span><i class="ri-store-line"></i></span>
                <h4>E-commerce Solutions</h4>
                <p>
                    We build secure, scalable, and user-centric online stores that
                    enhance the shopping experience and drive conversions.
                </p>
                </div>
                <div class="service__card">
                <span><i class="ri-smartphone-line"></i></span>
                <h4>Mobile Development</h4>
                <p>
                    From iOS to Android, we create apps that deliver seamless
                    performance and keep users coming back for more.
                </p>
                </div>
                <div class="service__card">
                <span><i class="ri-share-fill"></i></span>
                <h4>Content Marketing</h4>
                <p>
                    Our services include creating blog posts, videos, and social media
                    content that drives traffic and engagement.
                </p>
                </div>
                <div class="service__card">
                <span><i class="ri-seo-line"></i></span>
                <h4>SEO</h4>
                <p>
                    Our SEO strategies are tailored to your specific goals, helping you
                    reach your target audience and grow your online presence.
                </p>
                </div>
                <div class="service__card">
                <span><i class="ri-share-circle-line"></i></span>
                <h4>Digital Marketing</h4>
                <p>
                    From pay-per-click (PPC) advertising to social media marketing, we
                    ensure your brand stands out in the crowded digital landscape.
                </p>
                </div>
            </div>
            </section>

            <section class="section__container portfolio__container" id="portfolio">
            <h2 class="section__header">My Portfolio</h2>
            <p class="section__description">
                Explore a showcase of my diverse projects, demonstrating my skills in
                web development, design, and beyond. Each project reflects my passion
                for creating impactful and innovative digital experiences.
            </p>
            <div class="portfolio__grid">
                <div class="portfolio__card">
                <img src="assets/project-1.jpg" alt="portfolio" />
                </div>
                <div class="portfolio__card">
                <img src="assets/project-2.jpg" alt="portfolio" />
                </div>
                <div class="portfolio__card">
                <img src="assets/project-3.jpg" alt="portfolio" />
                </div>
                <div class="portfolio__card">
                <img src="assets/project-4.jpg" alt="portfolio" />
                </div>
                <div class="portfolio__card">
                <img src="assets/project-5.jpg" alt="portfolio" />
                </div>
                <div class="portfolio__card">
                <img src="assets/project-6.jpg" alt="portfolio" />
                </div>
            </div>
            <div class="portfolio__banner">
                <div class="portfolio__banner__card">
                <span><i class="ri-macbook-line"></i></span>
                <h4>150+ Projects</h4>
                <p>Delivered</p>
                </div>
                <div class="portfolio__banner__card">
                <span><i class="ri-discuss-line"></i></span>
                <h4>1500+ Happy</h4>
                <p>Customers</p>
                </div>
                <div class="portfolio__banner__card">
                <span><i class="ri-heart-fill"></i></span>
                <h4>2700+ Lovely</h4>
                <p>Feedbacks</p>
                </div>
            </div>
            </section>

            <section class="section__container contact__container" id="contact">
            <div class="logo">M</div>
            <h2 class="section__header">Let's Talk With Me!</h2>
            <p class="section__description">
                An open invitation to connect, and exploring collaborative opportunities
                on my personal portfolio website.
            </p>
            <div class="contact__socials">
                <a href="#"><i class="ri-twitter-fill"></i></a>
                <a href="#"><i class="ri-linkedin-fill"></i></a>
                <a href="#"><i class="ri-behance-fill"></i></a>
                <a href="#"><i class="ri-dribbble-line"></i></a>
                <a href="#"><i class="ri-pinterest-line"></i></a>
            </div>
            </section>
            <footer class="footer">
            Copyright © 2023 Web Design Mastery. All rights reserved.
            </footer>

            <script src="https://unpkg.com/scrollreveal"></script>
            <script src="main.js"></script>
        </body>
        </html>
        
    CSS:
        @import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap");

        :root {{
        --primary-color: #e9615e;
        --secondary-color: #ec9956;
        --extra-light: #f3f4f6;
        --white: #ffffff;
        --gradient-1: linear-gradient(to bottom right, #62393c, #181e41);
        --gradient-2: linear-gradient(
            to bottom,
            var(--primary-color),
            var(--secondary-color)
        );
        --max-width: 1200px;
        }}

        * {{
        padding: 0;
        margin: 0;
        box-sizing: border-box;
        }}

        .section__container {{
        max-width: var(--max-width);
        margin: auto;
        padding: 5rem 1rem;
        }}

        .section__header {{
        margin-bottom: 1rem;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        }}

        .section__description {{
        max-width: 600px;
        margin-inline: auto;
        color: var(--extra-light);
        text-align: center;
        line-height: 1.75rem;
        }}

        .btn {{
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 500;
        color: var(--white);
        background-image: var(--gradient-2);
        outline: none;
        border: none;
        border-radius: 5rem;
        cursor: pointer;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
        }}

        img {{
        width: 100%;
        display: flex;
        }}

        a {{
        text-decoration: none;
        }}

        .logo {{
        display: inline-block;
        padding: 10px 14px;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--white);
        background-image: var(--gradient-2);
        border-radius: 100%;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
        }}

        html,
        body {{
        scroll-behavior: smooth;
        }}

        body {{
        font-family: "Montserrat", sans-serif;
        color: var(--white);
        background-image: var(--gradient-1);
        }}

        nav {{
        position: fixed;
        isolation: isolate;
        top: 0;
        width: 100%;
        max-width: var(--max-width);
        margin: auto;
        z-index: 9;
        }}

        .nav__bar {{
        padding: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        background-image: var(--gradient-1);
        }}

        .nav__logo {{
        padding: 9px 12px;
        font-size: 1.2rem;
        }}

        .nav__bar a {{
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--white);
        }}

        .nav__menu__btn {{
        font-size: 1.5rem;
        color: var(--white);
        cursor: pointer;
        }}

        .nav__links {{
        list-style: none;
        position: absolute;
        width: 100%;
        padding: 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2rem;
        background-image: var(--gradient-2);
        transform: translateY(-100%);
        transition: 0.5s;
        z-index: -1;
        }}

        .nav__links.open {{
        transform: translateY(0);
        }}

        .nav__links a {{
        color: var(--white);
        transition: 0.3s;
        }}

        .nav__links a:hover {{
        color: var(--white);
        }}

        .btn__large {{
        display: none;
        }}

        .header__container {{
        padding-top: 8rem;
        display: grid;
        gap: 2rem;
        isolation: isolate;
        }}

        .header__content {{
        text-align: center;
        }}

        .header__content h1 {{
        margin-bottom: 1rem;
        font-size: 3rem;
        text-align: center;
        }}

        .header__content .section__description {{
        margin-bottom: 2rem;
        }}

        .header__image {{
        position: relative;
        isolation: isolate;
        z-index: -1;
        }}

        .header__image img {{
        max-width: 450px;
        margin-inline: auto;
        border-radius: 25rem;
        }}

        .header__image::after {{
        position: absolute;
        content: "MICHAEL";
        letter-spacing: 1.5rem;
        opacity: 0.5;
        right: 1rem;
        top: 50%;
        transform: translate(50%, -50%) rotate(90deg);
        }}

        .about__container {{
        display: grid;
        gap: 2rem;
        }}

        .about__image {{
        position: relative;
        isolation: isolate;
        max-width: 400px;
        margin: auto;
        }}

        .about__img {{
        border-radius: 100%;
        }}

        .about__bg-1,
        .about__bg-2 {{
        position: absolute;
        max-width: 150px;
        z-index: -1;
        }}

        .about__bg-1 {{
        top: 0;
        left: 0;
        }}

        .about__bg-2 {{
        right: 0;
        bottom: 0;
        }}

        .about__content {{
        text-align: center;
        }}

        .about__content .section__description {{
        margin-bottom: 2rem;
        }}

        .service__grid {{
        margin-top: 2rem;
        display: grid;
        gap: 1rem;
        }}

        .service__card {{
        padding: 2rem 1rem;
        text-align: center;
        background-image: var(--gradient-2);
        border-radius: 1rem;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
        }}

        .service__card span {{
        display: inline-block;
        margin-bottom: 1rem;
        font-size: 2rem;
        }}

        .service__card h4 {{
        margin-bottom: 1rem;
        font-size: 1.2rem;
        font-weight: 700;
        }}

        .service__card p {{
        color: var(--extra-light);
        line-height: 2rem;
        }}

        .portfolio__grid {{
        margin-top: 2rem;
        display: grid;
        gap: 1rem;
        }}

        .portfolio__card {{
        overflow: hidden;
        border-radius: 1rem;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
        }}

        .portfolio__card img {{
        transition: 0.5s;
        }}

        .portfolio__card:hover img {{
        transform: scale(1.1);
        }}

        .portfolio__banner {{
        margin-top: 2rem;
        padding: 2rem;
        display: grid;
        gap: 2rem;
        text-align: center;
        background-image: var(--gradient-2);
        border-radius: 1rem;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
        }}

        .portfolio__banner__card span {{
        display: inline-block;
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
        }}

        .portfolio__banner__card h4 {{
        font-size: 1.2rem;
        font-weight: 600;
        }}

        .portfolio__banner__card p {{
        font-weight: 500;
        }}

        .contact__container {{
        text-align: center;
        }}

        .contact__container .logo {{
        margin-bottom: 1rem;
        }}

        .contact__socials {{
        margin-top: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        }}

        .contact__socials a {{
        padding: 7px 10px;
        font-size: 1.5rem;
        color: var(--white);
        background: rgba(255, 255, 255, 0.2);
        border-radius: 100%;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.1);
        transition: 0.3s;
        }}

        .contact__socials a:hover {{
        background: var(--gradient-2);
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
        }}

        .footer {{
        padding: 1rem;
        font-size: 0.9rem;
        color: var(--extra-light);
        text-align: center;
        }}

        @media (width > 576px) {{
        .service__grid {{
            grid-template-columns: repeat(2, 1fr);
        }}

        .portfolio__grid {{
            grid-template-columns: repeat(2, 1fr);
        }}

        .portfolio__banner {{
            grid-template-columns: repeat(2, 1fr);
            text-align: left;
        }}
        }}

        @media (width > 768px) {{
        nav {{
            padding: 2rem 1rem;
            position: static;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .nav__bar {{
            padding: 0;
            background-image: none;
        }}

        .nav__menu__btn {{
            display: none;
        }}

        .nav__links {{
            padding: 0;
            width: unset;
            position: static;
            transform: none;
            flex-direction: row;
            background-image: none;
        }}

        .nav__links a:hover {{
            color: var(--secondary-color);
        }}

        .nav__links li:last-child {{
            display: none;
        }}

        .btn__large {{
            display: flex;
        }}

        .header__container {{
            padding-top: 5rem;
            grid-template-columns: repeat(4, 1fr);
            align-items: center;
        }}

        .header__image {{
            grid-area: 1/3/2/5;
        }}

        .header__image img {{
            margin-inline-start: unset;
        }}

        .header__content {{
            grid-area: 1/1/2/4;
            text-align: left;
        }}

        .header__content h1 {{
            font-size: 6rem;
            line-height: 6rem;
            text-align: left;
        }}

        .header__content .section__description {{
            text-align: left;
            margin-inline-start: unset;
        }}

        .about__container {{
            grid-template-columns: repeat(2, 1fr);
            align-items: center;
        }}

        .about__content,
        .about__content :is(.section__header, .section__description) {{
            text-align: left;
        }}

        .service__grid {{
            grid-template-columns: repeat(3, 1fr);
        }}

        .portfolio__container :is(.section__header, .section__description) {{
            text-align: left;
            margin-inline-start: unset;
        }}

        .portfolio__grid {{
            grid-template-columns: repeat(3, 1fr);
        }}

        .portfolio__banner {{
            grid-template-columns: repeat(3, 1fr);
        }}
    }}
    
    Javascript:
        const navLinks = document.getElementById("nav-links");
        const menuBtn = document.getElementById("menu-btn");
        const menuBtnIcon = menuBtn.querySelector("i");

        menuBtn.addEventListener("click", (e) => {{
        navLinks.classList.toggle("open");

        const isOpen = navLinks.classList.contains("open");
        menuBtnIcon.setAttribute(
            "class",
            isOpen ? "ri-close-line" : "ri-menu-3-line"
        );
        }});

        navLinks.addEventListener("click", (e) => {{
        navLinks.classList.remove("open");
        menuBtnIcon.setAttribute("class", "ri-menu-3-line");
        }});

        const scrollRevealOption = {{
        distance: "50px",
        origin: "bottom",
        duration: 1000,
        }};

        // header container
        ScrollReveal().reveal(".header__content h1", {{
        ...scrollRevealOption,
        }});

        ScrollReveal().reveal(".header__content .section__description", {{
        ...scrollRevealOption,
        delay: 500,
        }});

        ScrollReveal().reveal(".header__content .header__btn", {{
        ...scrollRevealOption,
        delay: 1000,
        }});

        // about container
        ScrollReveal().reveal(".about__content .section__header", {{
        ...scrollRevealOption,
        }});

        ScrollReveal().reveal(".about__content .section__description", {{
        ...scrollRevealOption,
        delay: 500,
        }});

        ScrollReveal().reveal(".about__content .about__btn", {{
        ...scrollRevealOption,
        delay: 1000,
        }});

        // service container
        ScrollReveal().reveal(".service__card", {{
        ...scrollRevealOption,
        interval: 500,
        }});

        // portfolio container
        ScrollReveal().reveal(".portfolio__card", {{
        duration: 1000,
        interval: 500,
        }});
    '''
    
    state["llm_messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    while True:
        response =  client.chat.completions.create(model= "gpt-5.1", response_format= {"type": "json_object"}, messages=state["llm_messages"])
        print("👌 ",response.choices[0].message.content)
        jsonOp = json.loads(response.choices[0].message.content)
        
        if jsonOp.get("step") == "ACTION":
            func = jsonOp.get("function")
            inputs = jsonOp.get("input")
            print(f"Calling the {func} function")
            tool_map[func](inputs)
            state["llm_messages"].append({"role": "assistant", "content": response.choices[0].message.content })
            continue
        
        if jsonOp.get("step") == "RESULT":
            print("\n\n Ouput:", jsonOp.get("content"))
            state["llm_messages"].append({"role":"assistant", "content": response.choices[0].message.content})
            state["llm_result"] = response.choices[0].message.content
            break
        state["llm_messages"].append({"role":"assistant", "content": response.choices[0].message.content})
        print(f'         {jsonOp.get("content")}')
    
    return state
# The conditional edges do not update the state

def flow_decide_resume_or_not(state: State) -> Literal["portfolio_from_resume", END]:
    print("🎶 flow_decide_resume_or_not")
    if state["is_resume"]:
        return "portfolio_from_resume"
    return END


# Graph node registry
# creating graph
graph_builder = StateGraph(State)

# registering the nodes
graph_builder.add_node("load_pdf", load_pdf)
graph_builder.add_node("check_if_resume_or_not",check_if_resume_or_not)
graph_builder.add_node("portfolio_from_resume",portfolio_from_resume)
graph_builder.add_node("flow_decide_resume_or_not", flow_decide_resume_or_not)


# Adding edges
graph_builder.add_edge(START, "load_pdf")
graph_builder.add_edge("load_pdf","check_if_resume_or_not")
graph_builder.add_conditional_edges("check_if_resume_or_not", flow_decide_resume_or_not)
graph_builder.add_edge("portfolio_from_resume", END)

# compiling the graph
graph = graph_builder.compile()

if __name__ == "__main__":
    state = {
        "file_path":  "../pdfs/Aniket_Hans_SWE_dev.pdf",
        "pdf_data": "",
        "user_name": "",
        "is_resume": False,
        "llm_result": "",
        "llm_messages": []
    }
    response = graph.invoke(state)
    print(response)

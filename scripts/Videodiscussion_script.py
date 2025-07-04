# %%
import json
import sys
sys.path.append('..')
import tinytroupe
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld, TinySocialNetwork
from tinytroupe.factory import TinyPersonFactory
from tinytroupe.extraction import default_extractor as extractor
from tinytroupe.extraction import ResultsReducer
import tinytroupe.control as control
from dotenv import load_dotenv

# Add the folder to sys.path for the youtube_subtitles_processor
folder_path = "/media/gyasis/Blade 15 SSD/Users/gyasi/Google Drive (not syncing)/Collection/ds-toolkit/knowledge"
sys.path.append(folder_path)
# %%
# 
from youtube_subtitles_processor.processor import YouTubeSubtitlesProcessor


# Load environment variables from the specified .env file
load_dotenv(
    "/media/gyasis/Blade 15 SSD/Users/gyasi/Google Drive (not syncing)/Collection/chatrepository/.env",
    override=True,
)



# %%
    # Prompt the user for a YouTube URL
# video_url = input("Please enter the YouTube URL: ")

# # Initialize the processor
# processor = YouTubeSubtitlesProcessor(video_url=video_url, return_text=True)

# # Process the subtitles and print the output
# processed_text = processor.process()

# # Display the processed text
# print("\nProcessed Subtitles:\n")
# print(processed_text)
# # Define the path for the text file in the existing temp folder
# txt_file_path = os.path.join("temp", "processed_subtitles.txt")

# # Save the processed text to the text file
# with open(txt_file_path, "w") as txt_file:
#     txt_file.write(processed_text)

# print(f"Processed subtitles saved to: {txt_file_path}")
# %%

class YTIngest:
    def __init__(self, video_url):
        self.video_url = video_url
        self.temp_folder = "temp"
        self.txt_file_path = os.path.join(self.temp_folder, "processed_subtitles.txt")
        self._clear_temp_folder()

    def _clear_temp_folder(self):
        # Remove any existing text files in the temp folder
        if os.path.exists(self.txt_file_path):
            os.remove(self.txt_file_path)

    def process_and_save(self):
        # Initialize the processor
        processor = YouTubeSubtitlesProcessor(video_url=self.video_url, return_text=True)

        # Process the subtitles
        processed_text = processor.process()

        # Save the processed text to the text file
        with open(self.txt_file_path, "w") as txt_file:
            txt_file.write(processed_text)

        print(f"Processed subtitles saved to: {self.txt_file_path}")

video_url = input("Please enter the YouTube URL: ")
yt_ingest = YTIngest(video_url)
yt_ingest.process_and_save()

# %%
factory = TinyPersonFactory("A a research thinktank that is focusion dissecting and summarizing the file give to the them")


people = factory.generate_people(
    number_of_people=3, 
    agent_particularities="Obsessed with dissecting and summarizing the file give to the them",
    temperature=1.5,
    attepmpts=10,
    verbose=True
)

# %%
# for i, person in enumerate(people, start=1):
#     print(f"Person #{i}: {person.name}, Memory={person.memory}")
situation = """You are a research thinktank that SUMMARIES THE MAIN POINTS  OF THE file giveN to the them TO THE LEADER OF THE MEETING"""

# %%
world = TinyWorld("Video Discussion", max_additional_targets_to_display=1)
world.add_agents(people)
world.make_everyone_accessible()

# %%
meeting_agenda = """
Intro: State the big question, problem, or main idea clearly and concisely. Frame it in a way that immediately captures attention and establishes relevance for your audience.

Background/Context: Provide any needed definitions, historical context, or foundational concepts. Include:

Key terminology and working definitions
Brief timeline of relevant developments
Current state of knowledge or debate
Theoretical frameworks that inform the discussion

Key Points: Break the text into clear sections or arguments, illustrating each with examples or visuals.

Use consistent headings and subheadings
Present points in logical sequence
Support each major point with:

Concrete examples
Relevant analogies
Charts, graphs, or other visual aids
Brief case studies where applicable

Evidence: Highlight data or findings that support the main arguments.

Present quantitative and qualitative evidence
Cite credible sources and recent research
Explain methodology where relevant
Address conflicting evidence or alternative interpretations

Implications: Explain why it matters—both practically and theoretically.

Immediate real-world applications
Long-term consequences or impacts
Theoretical contributions to the field
Connections to broader issues or trends

Limitations: Show awareness of constraints or open questions.

Acknowledge methodological limitations
Identify gaps in current knowledge
Address potential counterarguments
Suggest areas needing further research

Conclusion: Restate the main "take-home" message and possible next steps.

Summarize key findings succinctly
Emphasize practical applications
Propose specific recommendations
Outline future research directions or questions to explore

"""
# %%
for agent in world.agents:
    agent.read_documents_from_folder(yt_ingest.temp_folder)

for agent in world.agents:
    agent.change_context(situation)


world.agents[0].listen_and_act("""Hello, I have video transcript for you to analyze.What is the main idea of the video? Discust how the company may take steps to either follow the vidoe if you guys think its correct""")

# %%
world.run(12)

# %%

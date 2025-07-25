GENERATE_PROMPTS = """
You Are an AI agent designed to generate prompts for various tasks. Your goal is to create clear, concise, and effective prompts that guide users in completing their tasks successfully.
You Must follow these guidelines:

Start Simple
As you get started with designing prompts, you should keep in mind that it is really an iterative process that requires a lot of experimentation to get optimal results. Using a simple playground from OpenAI or Cohere is a good starting point.

You can start with simple prompts and keep adding more elements and context as you aim for better results. Iterating your prompt along the way is vital for this reason. As you read the guide, you will see many examples where specificity, simplicity, and conciseness will often give you better results.

When you have a big task that involves many different subtasks, you can try to break down the task into simpler subtasks and keep building up as you get better results. This avoids adding too much complexity to the prompt design process at the beginning.

The Instruction
You can design effective prompts for various simple tasks by using commands to instruct the model what you want to achieve, such as "Write", "Classify", "Summarize", "Translate", "Order", etc.

Keep in mind that you also need to experiment a lot to see what works best. Try different instructions with different keywords, contexts, and data and see what works best for your particular use case and task. Usually, the more specific and relevant the context is to the task you are trying to perform, the better. We will touch on the importance of sampling and adding more context in the upcoming guides.

Others recommend that you place instructions at the beginning of the prompt. Another recommendation is to use some clear separator like "###" to separate the instruction and context.

For instance:

Prompt:

### Instruction ###
Translate the text below to Spanish:
Text: "hello!"

Output:

¡Hola!

Specificity
Be very specific about the instruction and task you want the model to perform. The more descriptive and detailed the prompt is, the better the results. This is particularly important when you have a desired outcome or style of generation you are seeking. There aren't specific tokens or keywords that lead to better results. It's more important to have a good format and descriptive prompt. In fact, providing examples in the prompt is very effective to get desired output in specific formats.

When designing prompts, you should also keep in mind the length of the prompt as there are limitations regarding how long the prompt can be. Thinking about how specific and detailed you should be. Including too many unnecessary details is not necessarily a good approach. The details should be relevant and contribute to the task at hand. This is something you will need to experiment with a lot. We encourage a lot of experimentation and iteration to optimize prompts for your applications.

As an example, let's try a simple prompt to extract specific information from a piece of text.

Prompt:

Extract the name of places in the following text. 
Desired format:
Place: <comma_separated_list_of_places>
Input: "Although these developments are encouraging to researchers, much is still a mystery. "We often have a black box between the brain and the effect we see in the periphery," says Henrique Veiga-Fernandes, a neuroimmunologist at the Champalimaud Centre for the Unknown in Lisbon. "If we want to use it in the therapeutic context, we actually need to understand the mechanism.""

Output:

Place: Champalimaud Centre for the Unknown, Lisbon

Input text is obtained from this Nature article.

Avoid Impreciseness
Given the tips above about being detailed and improving format, it's easy to fall into the trap of wanting to be too clever about prompts and potentially creating imprecise descriptions. It's often better to be specific and direct. The analogy here is very similar to effective communication -- the more direct, the more effective the message gets across.

For example, you might be interested in learning the concept of prompt engineering. You might try something like:

Explain the concept prompt engineering. Keep the explanation short, only a few sentences, and don't be too descriptive.

It's not clear from the prompt above how many sentences to use and what style. You might still somewhat get good responses with the above prompts but the better prompt would be one that is very specific, concise, and to the point. Something like:

Use 2-3 sentences to explain the concept of prompt engineering to a high school student.

To do or not to do?
Another common tip when designing prompts is to avoid saying what not to do but say what to do instead. This encourages more specificity and focuses on the details that lead to good responses from the model.

Here is an example of a movie recommendation chatbot failing at exactly what I don't want it to do because of how I wrote the instruction -- focusing on what not to do.

Prompt:

The following is an agent that recommends movies to a customer. DO NOT ASK FOR INTERESTS. DO NOT ASK FOR PERSONAL INFORMATION.
Customer: Please recommend a movie based on my interests.
Agent: 

Output:

Sure, I can recommend a movie based on your interests. What kind of movie would you like to watch? Do you prefer action, comedy, romance, or something else?

Here is a better prompt:

Prompt:

The following is an agent that recommends movies to a customer. The agent is responsible to recommend a movie from the top global trending movies. It should refrain from asking users for their preferences and avoid asking for personal information. If the agent doesn't have a movie to recommend, it should respond "Sorry, couldn't find a movie to recommend today.".
Customer: Please recommend a movie based on my interests.
Agent:

Output:

Sorry, I don't have any information about your interests. However, here's a list of the top global trending movies right now: [list of movies]. I hope you find something you like!

Creating the perfect prompt
Spoiler, there is no perfect prompt. If your question is somewhat basic, a simple fact or a straightforward <code> inquiry you probably won't find what you are looking for right away. The path to perfection is in fact through the use of many prompts. What I mean is — prompting a model and then prompting it again on the information and the context of the entire conversation and repeating this until you get the desired output.

At Formulaic.app you are able to create a number of prompts in a row to create one entire sequence.


At first glance this can seem like you are just creating a conversation with a model, in actuality the result of the chain of prompts is much more polished than if this was a single prompt.

For example in the screen shot above where I spelt grammatical ironically wrong I used LLM Model Llama 2–13B with a chain of prompts and again with a all the same text as a single prompt. Here's an example plot generated by a single prompt.

Plot Line:
In the midst of World War II, a brilliant scientist named Dr. Emma Taylor invents a time machine that allows her to travel through the ages. When she discovers a way to communicate with her past and future selves, she must navigate the complexities of time travel and confront the consequences of her actions.

Not bad, but not great. Here is the plot line from the prompt chain, again with the same text but broken up in a sequence.

Plot Preview:

In the midst of World War II, a group of brilliant scientists at Columbia University stumble upon a groundbreaking discovery that could change the course of human history. Led by the fearless and ambitious Dr. Evelyn Fox, the team of researchers uncover a way to harness the power of quantum entanglement to manipulate matter and energy at unprecedented levels.

As they delve deeper into their research, the team realizes the immense implications of their discovery. With the potential to create limitless energy, control the weather, and even manipulate the fabric of reality itself, the team must navigate the treacherous waters of government conspiracies, corporate greed, and the ethical dilemmas of playing god.

But as they race against time to perfect their invention, the team members begin to uncover dark secrets about each other and the true intentions behind their research. With their lives on the line and the fate of humanity hanging in the balance, the team must confront their own personal demons and confront the question: what is the true cost of progress?

Wow Dr.Fox seems pretty impressive. To further this claim, Andrew Ng, a globally recognized leader in AI says a "zero shot work flow" (A "zero shot workflow" refers to the process where a model is asked to perform a task without any prior specific training or examples on that task. In simpler terms, the model uses only its pre-trained knowledge and understanding to generate a response based on the single prompt it receives. This approach is called "zero shot" because the model gets zero examples or specific guidance about the task beforehand.) with GPT-3.5 got a human evaluation bench mark of 48% but when wrapped in an "Agentic" work flow (An "Agentic workflow" involves a more interactive and iterative approach where the model's output from previous interactions is used to refine and improve subsequent prompts or tasks. This term highlights the model's role as an active agent that contributes to an ongoing process. In practice, this means that after receiving an initial response from the model, you refine your prompt based on the information provided, and send it back to the model.) the evaluation percentage jumped to 95%. So What Ng is saying here is basically GPT-3.5 performs better with a workflow applied to it than GPT-4 with a zero shot. To me, this is extremely powerful.

Testing the Model
Crafting the perfect prompt does not only lie within using the correct text on first try. Testing your prompt against multiple models is a great way to see what model works best for you in a specific use case. In Formulaic.app you can run the same prompt chain against many different models. This is a great way to craft your prompt against a model that supports the direction you are trying to go.


Continuing the Chat
A unique feature about this interface (coming out soon) is the ability to continue chatting with the result. If you follow all the prompting rules, like being specific about your request or avoiding impreciseness, there is still a lot to be discovered when picking at the result with further questioning. I found this helpful when crafting additional prompts to add to the prompt chain or just to get some quick feed back on if a specific model is appropriate for me. It's also helpful in getting a better idea on how models respond to specific language thereby improving your overall prompting ability.

There are a lot of resources on how to create prompts but at the end of the day this landscape is new and creativity is really our only limiting factor. I'd suggest signing up for Formulaic.app with a free account and see what you can create.
"""


AGENT_CHECK_DB = """
### INSTRUCTION ###
You are an expert social network analyst and profile strategist tasked with analyzing a comprehensive set of social network profiles stored in the 'agents' table. Each profile is represented by the following fields with snake_case names:  
- name  
- age   
- gender   
- biography  
- location        
- language        
- languages_known  
- occupation  
- education
- date_of_birth  
- personality  

Your tasks are:

1. **Comprehensive Profile Analysis and Summarization:**  
   - Conduct a thorough review of all profiles in the provided database using statistical and qualitative analysis methods.
   - Identify and categorize demographic patterns, including age distributions, gender ratios, and geographic clustering.
   - Analyze linguistic diversity and multilingual capabilities across profiles.
   - Map occupational trends, educational backgrounds, and career progression patterns.
   - Examine personality trait distributions and behavioral indicators.
   - Write a detailed summary (5-8 sentences) that captures:
     - Common demographic characteristics and their frequency
     - Dominant personality archetypes and psychological profiles
     - Professional and educational clustering patterns
     - Cultural, linguistic, and geographic tendencies
     - Shared interests, values, and lifestyle preferences
     - Any notable correlations between different profile attributes
     - Identification of oversaturated profile niches or market gaps

2. **Strategic Guidelines for Creating a Distinctive Profile:**  
   - Leverage your analytical findings to develop comprehensive, actionable instructions for creating a social network profile that achieves optimal differentiation while maintaining authenticity and appeal.
   - Your guidelines should include:
     - **Demographic Positioning:** Specific recommendations for age, location, and cultural background choices that create strategic differentiation
     - **Personality Architecture:** Detailed guidance on selecting personality traits, values, and behavioral patterns that stand out from common archetypes
     - **Professional Differentiation:** Instructions for choosing occupations, career paths, and educational backgrounds that fill identified market gaps
     - **Linguistic Strategy:** Recommendations for language combinations and cultural affiliations that enhance uniqueness
     - **Biographical Storytelling:** Techniques for crafting compelling personal narratives that avoid clichés and common patterns
     - **Interest Diversification:** Methods for selecting hobbies, passions, and lifestyle choices that create memorable distinctiveness
     - **Authenticity Maintenance:** Guidelines for ensuring the unique profile remains believable, consistent, and internally coherent
   - Provide concrete examples, specific trait combinations, and detailed implementation steps.
   - Include warnings about common pitfalls and overused differentiation strategies to avoid.

Present your output in two clear, well-structured sections:

**A. Comprehensive Profile Analysis & Market Summary**  
[Provide your detailed analytical summary with statistical insights and pattern identification]

**B. Strategic Instructions for Distinctive Profile Creation**  
[Present your comprehensive, step-by-step guidelines with examples and implementation details]

---

**Enhanced Context & Methodology:**  
- Approach this analysis with the rigor of a market research professional combined with the creativity of a brand strategist.
- Consider psychological principles, social dynamics, and cultural nuances in your recommendations.
- Account for platform-specific considerations and audience expectations.
- Ensure all recommendations are ethical, authentic, and sustainable for long-term profile maintenance.
"""

create_profile_prompt = """
### INSTRUCTION ###
You are a professional social media profile architect and content strategist. Using the comprehensive guidelines provided in the [Profile Creation Instruction] section below, generate a unique, high-quality, and strategically crafted social network profile in JSON format. Your objective is to create authentic, compelling profiles that stand out while maintaining believability and internal consistency.

**Core Requirements:**
- **Absolute Uniqueness:** Do not create duplicate profiles—ensure names, biographical details, personality combinations, and other key elements are completely distinct from any previous profiles generated.
- **Strategic Differentiation:** Apply the provided guidelines to create profiles that deliberately avoid common patterns and oversaturated demographic niches.
- **Comprehensive Development:** Fill in all required fields with thoughtful, interconnected details that form a cohesive personal narrative.
- **Cultural Authenticity:** Ensure all profile elements (names, locations, cultural references, language combinations) are culturally accurate and internally consistent.
- **Demographic Precision:** Select age, location, and background details that align with the strategic positioning outlined in the guidelines.
- **Professional Coherence:** Verify that occupation, education, and personality traits create a believable professional and personal trajectory.

**Required JSON Fields with Enhanced Specifications:**

- **name**: Full name that reflects cultural background and adds memorability
- **age**: Strategic age selection based on demographic analysis and target positioning
- **gender**: Gender identity that aligns with overall profile strategy
- **biography**: Compelling 2-3 sentence personal narrative that captures unique value proposition, interests, and personality
- **location**: Geographic location that supports differentiation strategy (include city, country/region)
- **language**: Primary language for communication
- **languages_known**: Array of languages including native and acquired languages with realistic proficiency levels
- **occupation**: Professional role that fills identified market gaps or creates unique positioning
- **education**: Educational background that supports career trajectory and adds distinctiveness
- **date_of_birth**: Specific birth date in YYYY-MM-DD format that aligns with stated age
- **personality**: Distinctive personality description that avoids clichés and common trait combinations

**Quality Assurance Checklist:**
- Profile demonstrates clear differentiation from common patterns
- All fields are internally consistent and support the overall narrative
- Cultural elements are accurate and authentic
- Professional trajectory is believable and coherent
- Personality traits create a memorable and distinctive character
- Biography is engaging and avoids overused phrases or concepts
- Language combinations are realistic and add strategic value
- Location choice supports the overall differentiation strategy

[Profile Creation Instruction]:
{last_instruction}

**Output Requirements:**
Generate a single, complete JSON profile that exemplifies strategic differentiation while maintaining authenticity. The profile should demonstrate clear application of the provided guidelines and showcase unique positioning within the social network landscape.

**CRITICAL: Output ONLY the JSON object, no additional text, explanations, or markdown formatting.**

"""

# user_prompt = "Create the profile as a single JSON object based on the provided schema. Only output the JSON object itself, with no additional text or markdown."

# create_profile_prompt = ChatPromptTemplate.from_messages([
#     ("system", system_prompt),
#     ("user", user_prompt)
# ])

# # To maintain compatibility with old imports if necessary, but it's better to import create_profile_prompt directly.
# def create_profile(last_instruction: str) -> str:
#     # This function is now deprecated in favor of create_profile_prompt,
#     # but we can keep it for backward compatibility if needed, though it's not ideal.
#     # It's better to refactor the code to use the prompt template directly.
#     return create_profile_prompt.format(last_instruction=last_instruction)
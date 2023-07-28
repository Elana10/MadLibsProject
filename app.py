from flask import Flask, request, render_template
from flask_debugtoolbar import DebugToolbarExtension
import re 

app = Flask(__name__)
app.config['SECRET_KEY'] = "madlibstest"
debug = DebugToolbarExtension(app)

"""Madlibs Stories."""

class Story:
    """Madlibs story.

    To  make a story, pass a list of prompts, and the text
    of the template.

        >>> s = Story(["noun", "verb"],
        ...     "I love to {verb} a good {noun}.")

    To generate text from a story, pass in a dictionary-like thing
    of {prompt: answer, promp:answer):

        >>> ans = {"verb": "eat", "noun": "mango"}
        >>> s.generate(ans)
        'I love to eat a good mango.'
    """

    def __init__(self, words, text):
        """Create story with words and template text."""

        self.prompts = words
        self.template = text

    def generate(self, answers):
        """Substitute answers into text.
        
        I edited it slightly to ensure that inputs with a corresponging identical part of speech would be accessible.

        The answers variable is a dictionary with parts-of-speech and corresponding list of answers.
        Example: answers =  {'noun' : ['house','cup','ball'],
                             'verb' : ['play'],
                             'plural noun' : ['cats','cars']
                            }
        """


        text = self.template

        for (key, vals) in answers.items():
            # This will look at the part of speech noun/verb and then access the vals list associated
            for val in vals: 
                # This will roll through the list of values, from the example in the docs: house, cup, ball
                text = text.replace("{" + key + "}", val,1)
                # This will cycle through the text and replace the instances of the part of speech in order. In the text: {noun} == 'house' and the next {noun} == cup

        return text


# Here's a story to get you started



story_list = []
# global variable used to store the completed stories. 
story = Story(
    ["place", "noun", "verb", "adjective", "plural_noun"],
    """Once upon a time in a long-ago {place}, there lived a
       large {adjective} {noun}. It loved to {verb} {plural_noun}.""")
current_story = story
# global variable used to store the users created story. This will be replaced every time a new created story is entered. 

@app.route('/')
def root():
    # Takes you to the home page
    return render_template("base.html")

@app.route('/form', methods = ['GET', 'POST'])
def our_story():
    # If using 'get' from selecting the anchor 'Our Mad Lib Story' the global hard coded story variable is used to create a form to complete 
    # If using 'post' through the form submit button - the input responses are grabbed and the Story Class function .generate() is used to return text of the story. The text is saved in a global list variable 'story_list.' Then the global story list is reversed and passed off to the results.html page for rendering.  

    global story

    if request.method == 'POST':
        #Collect the user's responses as a dictionary
        user_responses = {}
        for prompt in story.prompts:
            # accesses the part-of-speech list from the Story class variable. 
            responses_list = request.form.getlist(prompt)
            # creates a list of all responses from the input fields that are labeled with the 'prompt' part-of-speech
            user_responses[prompt] = responses_list
            # builds the dictionary out with the {prompt-part-of-speech : [response1, response2, ...]}
            
        generated_story = story.generate(user_responses)
        # uses the class function .generate() to return a string of the new story. 
        story_list.append(generated_story)
        # saves the new story in a global list variable
        print_stories = reversed(story_list)

        return render_template('results.html', stories = print_stories)

    return render_template("form.html", story = story)

@app.route('/create', methods= ['GET', 'POST'])
def create():

    global current_story

    if request.method == 'GET':
        return render_template("create.html")
    
    user_text = request.form['new_story_input']
    # grabs the text from the form input with name new_story_input
    user_text = str(user_text)
    # makes sure that this is a string and not string like object
    pattern = r'\{([^}]*)\}'
    # creates a pattern key that will be used to search the text-- the pattern to look for is anything found within curly brackets {}
    word_prompt = re.findall(pattern, user_text)
    # creates a list based on the user_text with strings found inside the pattern


    current_story = Story(word_prompt,user_text)
    # saves the user's story into a global Story class variable to be used on the formuser and results page

    return render_template('formuser.html', story = current_story)

@app.route('/formuser', methods = ['GET', 'POST'])
def your_story_fill():
    # see form coding above with more time and direction.. I would find a way to eliminate the redunant code. 

    global current_story

    if request.method == 'POST':
        #Collect the user's responses as a dictionary
        user_responses = {}
        for prompt in current_story.prompts:
            responses_list = request.form.getlist(prompt)
            user_responses[prompt] = responses_list
            
        generated_story = current_story.generate(user_responses)
        story_list.append(generated_story)
        print_stories = reversed(story_list)

        return render_template('results.html', stories = print_stories)

    return render_template("formuser.html", story = current_story)


@app.route('/results')
def results():
    global story_list
    print_stories = reversed(story_list)

    return render_template("results.html", stories = print_stories)
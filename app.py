import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt, mpld3
from flask import Flask, send_file, json, render_template
import praw
from wordOps import countWords, punctRm, excludeWordsList
from config import RedditConfig

# Send "public/any.name" when route "<site>.com/{any.name}" is hit
app = Flask(__name__, static_url_path="", static_folder="static", template_folder='templates')

# Initialize PRAW (reddit wrapper) from config.py
# DO NOT push config.py to github, we do not want to
# make the API keys public.
# The format of config.py is:
#
# class RedditConfig:
#     id = '<client_id>'
#     secret = '<client_secret>'
#     userAgent = '<user_agent>'
reddit = praw.Reddit(client_id=RedditConfig.id,
                     client_secret=RedditConfig.secret,
                     user_agent=RedditConfig.userAgent)


# Remap '/' to index. Other files can be served statically.
@app.route('/')
def index():
	return render_template('index.html', chart="""
	Welcome to Seeing Redd. 
	Please navigate to 
	<a>/r/{subreddit-name}/hot</a>
	or
	<a>/u/{username}</a>
	to see more.
	""")

def newPosts(searchbase):
	return searchbase.new(limit=100)

def hotPosts(searchbase):
	return searchbase.hot(limit=100)

def topPostsAllTime(searchbase):
	return searchbase.top(time_filter='all', limit=100)
	
def topPostsPast24Hours(searchbase):
	return searchbase.top(time_filter='day', limit=100)

def controversialPostsAllTime(searchbase):
	return searchbase.controversial(time_filter='all', limit=100)
	
def controversialPast24Hours(searchbase):
	return searchbase.controversial(time_filter='day', limit=100)

switch = {"new": lambda x: newPosts(x),
		  "hot": lambda x: hotPosts(x),
		  "topalltime": lambda x: topPostsAllTime(x),
		  "top24hrs": lambda x: topPostsPast24Hours(x),
		  "controversialall": lambda x: controversialPast24Hours(x),
		  "controversial24hrs": lambda x: controversialPast24Hours(x),
}

@app.route('/r/<sr>/contributors/<category>')
def contributorsToSubreddit(sr, category):
	funct = switch.get(category)
	subreddit = reddit.subreddit(sr)
	submissions = funct(subreddit)
	contributers = filter(lambda x: x != None, [x.author for x in submissions])
	return render_template('index.html', data=contributers)

	

@app.route('/r/<sr>/<category>')
def wordCountSubreddit(sr, category):
	funct = switch.get(category)
	subreddit = reddit.subreddit(sr)
	submissions = funct(subreddit)
	posts = list(map(lambda x: x.selftext + " " + x.title, submissions))
	sortedWords = countWords(posts, punctRm, excludeWordsList)
	sortedWords = sortedWords[:50]
	labels = list()
	values = list()
	for word in sortedWords:
		labels.append(word[0])
		values.append(word[1])

	fig = plt.figure()
	if sortedWords:
	# Generate Chart
		plt.subplot(1, 2, 1)
		plt.bar(range(len(labels)), values, tick_label=labels)
		ax1 = fig.add_subplot(121) #changed from 111
		fig.subplots_adjust(top=0.85)
		ax1.set_xlabel('Word')
		y_rotate=ax1.set_ylabel('Instances')
		y_rotate.set_rotation(0)
	# Generate Word Cloud
		plt.subplot(1, 2, 2) #originally 122
		text = str(sortedWords)
		text = text.replace("'", "")
		wordcloud = WordCloud(width=480, height=480, margin=0).generate(text)
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis("off")
		plt.margins(x=0, y=0)
	else:
		plt.text(0.5,0.5,'stuff')
		#placeholder until we have a useful empty result page

	return render_template('index.html', chart=mpld3.fig_to_html(fig))

#word popularity by user
@app.route('/u/<user>/<category>')
def wordCountUser(user, category):
	user = reddit.redditor(name=user)
	comments = user.comments
	submissions = user.submissions
	funct = switch.get(category)
	commentWords = funct(comments)
	submissionWords = funct(submissions)
	usersText = list()
	for comment in commentWords:
		usersText.append(comment.body)
	for sub in submissionWords:
		usersText.append(sub.selftext)
	sortedWords = countWords(usersText, punctRm, excludeWordsList)
	sortedWords = sortedWords[:50]
	labels = list()
	values = list()
	for word in sortedWords:
		labels.append(word[0])
		values.append(word[1])
	
	fig = plt.figure()
	if sortedWords:
	# Generate Chart
		plt.subplot(1, 2, 1) #change to specific one
		plt.bar(range(len(labels)), values, tick_label=labels)
		ax1 = fig.add_subplot(121)
		fig.subplots_adjust(top=0.85)
		ax1.set_xlabel('Word')
		y_rotate=ax1.set_ylabel('Instances')
		y_rotate.set_rotation(0)
	# Generate Word Cloud
		plt.subplot(1,2,2) #originally 122
		text = str(sortedWords)
		text = text.replace("'", "")
		wordcloud = WordCloud(width=480, height=480, margin=0).generate(text)
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis("off")
		plt.margins(x=0, y=0)
	else:
		plt.text(0.5,0.5,'stuff')
		#placeholder until we have a useful empty result page
	
	#username=reddit.redditor(user)
	result="<div style='width: 100%; overflow: hidden;'>"
	result+="<div style='width:49%; float: left;'> <h3> Best Comment </h3> <p>"+ next(user.comments.top()).body +"</p> </div>"
	result+="<div style='margin-left:50%'> <h3> Worst Comment </h3> <p>"+ next(user.comments.top()).body +"</p> </div>"
	result+= "</div>"
	result+=mpld3.fig_to_html(fig)

	return render_template('index.html', chart=result)



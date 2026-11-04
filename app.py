from flask import Flask, render_template, request, jsonify
import PyPDF2, docx, json, os

app = Flask(__name__)

with open('catalogue.json') as f:
	PROGRAMS = json.load(f)

SKILLS = [
	"HTML", "CSS", "JavaScript", "React", "Responsive Design", "Python",
	"Flask", "SQL", "REST APIs", "Git", "Machine Learning", "Pandas",
	"NumPy", "Scikit-Learn", "Data Analysis", "Tableau", "Statistics",
	"Flutter", "Dart", "Firebase", "UI/UX Basics", "Docker", "Linux",
	"AWS", "CI/CD", "Deep Learning", "TensorFlow", "Figma", "UI Design",
	"UX Research", "Wireframing", "Prototyping",
]


def parse_cv(path):
	text = ""
	try:
		if path.endswith('.pdf'):
			reader = PyPDF2.PdfReader(path)
			for page in reader.pages:
				text += page.extract_text() or ""
		else:
			document = docx.Document(path)
			text = "\n".join(paragraph.text for paragraph in document.paragraphs)
	except Exception:
		pass
	return text


def extract(text):
	return list({skill for skill in SKILLS if skill.lower() in text.lower()})


def calc(user, program):
	required = program['required_skills']
	user_skills = {skill.lower() for skill in user}
	matched = [skill for skill in required if skill.lower() in user_skills]
	missing = [skill for skill in required if skill.lower() not in user_skills]
	score = int((len(matched) / len(required)) * 100) if required else 0
	return {
		"program": program,
		"score": min(92, score),
		"matching_skills": matched,
		"missing_skills": missing,
		"why": (
			f"Your selected {', '.join(matched)} closely match this program's prerequisites."
			if matched else "Based on profile fit."
		),
	}


@app.route('/')
def home():
	return render_template('index.html')


@app.route('/catalogue.json')
def cat():
	return jsonify(PROGRAMS)


@app.route('/api/parse', methods=['POST'])
def pars():
	uploaded_file = request.files['cv']
	path = 'temp_' + uploaded_file.filename
	uploaded_file.save(path)
	text = parse_cv(path)
	os.remove(path)
	return jsonify({"extracted_skills": extract(text)})


@app.route('/api/match', methods=['POST'])
def mat():
	skills = request.json.get('skills', [])
	results = sorted(
		[calc(skills, program) for program in PROGRAMS],
		key=lambda result: result['score'],
		reverse=True,
	)[:3]
	return jsonify({"matches": results})


if __name__ == '__main__':
	app.run(debug=True)

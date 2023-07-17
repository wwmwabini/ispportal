from ispportal import app, scheduler


if __name__ == "__main__":
	app.run(debug=True, port=5028, host="0.0.0.0")
from app import app
from sys import argv

if __name__ == '__main__':
	try:
		# Get Port
		port = 8081
		if len(argv) > 1:
			port = int(argv[1])

		# Serve
		app.run(host='0.0.0.0', port=port, debug=True)

	except Exception as e:
		print("Something went wrong, process terminated...")
		print("Error Report: " + str(e))

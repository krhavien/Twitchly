from http.server import HTTPServer, BaseHTTPRequestHandler
import twitch_user as twitch_user
import twitchly_db as twitchly_db

db = twitchly_db.Database()

class Serv(BaseHTTPRequestHandler):
    
    def process(self, user):
        output = "Processing data for: " + user
        user_id = twitch_user.get_user_id(user)
        data = db.get_user_info(user_id)
        return output + "\n" + str(data)

    def do_GET(self):
        filePath = '/index.html' if self.path == '/' else self.path
        if '/?username=' in self.path:
            user = self.path[11:]
            fileContent = bytes(self.process(user), 'utf-8')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(fileContent)
            return
        filePath = filePath.replace('%20', ' ') # this line allows files and directories which contains spaces in their names
        try:
            with open(filePath[1:], 'rb') as file: # this line open the file to be read as binary (done by 'rb'), images has to be read as binary
                fileContent = file.read()
            self.send_response(200)
        except:
            fileContent = bytes('File not found!', 'utf-8')
            self.send_response(404)
        self.end_headers()
        self.wfile.write(fileContent)


httpd = HTTPServer(('localhost', 8000), Serv)
print("serving on http://localhost:8000")
httpd.serve_forever()


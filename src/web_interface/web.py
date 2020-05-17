from flask import Flask, render_template
from os import walk

app = Flask( __name__ )

ROOT_DIR = "../../"

@app.route('/')
def index():
    fandoms = []
    (_, fandoms, _) = next(walk(ROOT_DIR + "fandoms/"))
    print(fandoms)
    
    return render_template( "index.html", fandoms=fandoms )

if __name__ == '__main__':
    app.run( debug=True )
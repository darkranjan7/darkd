from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import json
import time

app = Flask(__name__)
CORS(app)

@app.route('/stream-formats')
def stream_formats():
    url = request.args.get('url')
    
    def generate():
        try:
            # Initial progress
            yield f"data: {json.dumps({'type': 'progress', 'progress': 10, 'message': 'Connecting to YouTube...'})}\n\n"
            time.sleep(0.5)  # Simulate processing time
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            # Extracting info progress
            yield f"data: {json.dumps({'type': 'progress', 'progress': 30, 'message': 'Extracting video information...'})}\n\n"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []
                
                # Processing formats progress
                yield f"data: {json.dumps({'type': 'progress', 'progress': 60, 'message': 'Processing available formats...'})}\n\n"
                
                for f in info['formats']:
                    format_info = {
                        'format_id': f.get('format_id', 'N/A'),
                        'ext': f.get('ext', 'N/A'),
                        'resolution': f.get('resolution', 'N/A'),
                        'filesize': f.get('filesize', 0),
                        'url': f.get('url', ''),
                        'type': 'Audio Only' if f.get('vcodec') == 'none' else 
                               'Video Only' if f.get('acodec') == 'none' else 
                               'Video+Audio'
                    }
                    formats.append(format_info)
                
                # Final progress and data
                yield f"data: {json.dumps({'type': 'progress', 'progress': 100, 'message': 'Complete!'})}\n\n"
                yield f"data: {json.dumps({'type': 'complete', 'formats': formats})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/')
def hello_world():
    return jsonify({"message": "hello world"})

@app.route('/greet', methods=['POST'])
def greet_user():
    data = request.get_json()
    name = data.get('name', 'stranger')
    return jsonify({"message": f"Hello {name}!"})

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url')
        
        ydl_opts = {
            'format': 'best',  # Get best quality
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info['url']
            
        return jsonify({
            "status": "success",
            "download_url": download_url
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@app.route('/formats', methods=['POST'])
def get_formats():
    try:
        data = request.get_json()
        url = data.get('url')
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            for f in info['formats']:
                format_info = {
                    'format_id': f.get('format_id', 'N/A'),
                    'ext': f.get('ext', 'N/A'),
                    'resolution': f.get('resolution', 'N/A'),
                    'filesize': f.get('filesize', 0),
                    'url': f.get('url', ''),
                    'type': 'Audio Only' if f.get('vcodec') == 'none' else 
                           'Video Only' if f.get('acodec') == 'none' else 
                           'Video+Audio'
                }
                formats.append(format_info)
            
        return jsonify({
            "status": "success",
            "formats": formats,
            "title": info.get('title', 'Unknown')
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
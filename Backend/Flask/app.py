from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
import subprocess

app=Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///A:\web scrapper\Backend\Flask\data.db'

db=SQLAlchemy(app)


class ProdResult(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(1000))
	img = db.Column(db.String(1000))
	url = db.Column(db.String(2000))
	price = db.Column(db.Float)
	created_at = db.Column(db.DateTime, default=datetime.now())
	search_text = db.Column(db.String(255))
	source = db.Column(db.String(255))

	def __init__(self, name, img, url, price, search_text, source):
		self.name = name
		self.url = url
		self.img = img
		self.price = price
		self.search_text = search_text
		self.source = source


class TrackedProd(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(1000))
	created_at = db.Column(db.DateTime, default=datetime.now())
	tracked = db.Column(db.Boolean, default=True)

	def __init__(self, name, tracked=True):
		self.name = name
		self.tracked = tracked



@app.route('/results',methods=['POST'])
def submit_results():
	results=request.json.get('data')
	search_text=request.json.get('search_text')
	source=request.json.get('source')

	for result in results:
		product_result = ProdResult(
			name=result['name'],
			url=result['url'],
			img=result["img"],
			price=result['price'],
			search_text=search_text,
			source=source
		)
		db.session.add(product_result)

	db.session.commit()
	response = {'message': 'Received data successfully'}
	return jsonify(response), 200


def get_unique_search_txt():
	unique_serch_txt=db.session.query(
		ProdResult.search_text).distinct().all()
	unique_serch_txt=[text[0] for text in unique_serch_txt]
	return unique_serch_txt

@app.route('/unique_search_texts',methods=['GET'])
def get_unique():
	unique_search_texts=get_unique_search_txt()
	return jsonify(unique_search_texts),200

@app.route('/results')
def get_prd_results():
	srch_txt=request.args.get('search_text')
	results=ProdResult.query.filter_by(search_text=srch_txt).order_by(ProdResult.created_at.desc()).all()

	prd_dict={}
	for result in results:
		url=result.url
		if url not in prd_dict:
			prd_dict[url]={
				'name':result.name,
				'url':result.url,
				'img':result.img,
				'source':result.source,
				'created_at':result.created_at,
				'priceHistory':[]
			}
		prd_dict[url]['priceHistory'].append({
			'price':result.price,
			'date':result.created_at
		})


	results1=list(prd_dict.values())

	return jsonify(results1),200


@app.route('/all-results',methods=['GET'])
def get_results():
	results=ProdResult.query.all()
	prd_reslts=[]
	for result in results:
		prd_reslts.append({
			'name': result.name,
			'url': result.url,
			'price': result.price,
			"img": result.img,
			'date': result.created_at,
			"created_at": result.created_at,
			"search_text": result.search_text,
			"source": result.source
		})
	return jsonify(prd_reslts),200





@app.route('/start-scraper',methods=['POST'])
def start_scraper():
	url=request.json.get('url')
	search_text=request.json.get('search_text')

	prev_results=get_unique_search_txt()
	if search_text in prev_results:
		response={"message":"Product already scrapped"}
		return jsonify(response),409
	else:
		command = f"python ./Flask/scraper/__init__.py {url} \"{search_text}\" /results"
		subprocess.Popen(command, shell=True)
		response={"message":"scraper started"}
		return jsonify(response),200


@app.route('/add-tracked-product',methods=['POST'])
def add_tracked_product():
	name=request.json.get('name')
	trcked_prd=TrackedProd(name=name)
	db.session.add(trcked_prd)
	db.session.commit()

	response={"message":"Tracked product added successfully","id":trcked_prd.id}
	return jsonify(response),200


@app.route('/tracked-products',methods=['GET'])
def get_tracked_products():
	trck_prd=TrackedProd.query.all()
	results=[]
	for prd in trck_prd:
		results.append({
			'id':prd.id,
			'name':prd.name,
			'created_at':prd.created_at,
			'tracked':prd.tracked
		})

	return jsonify(results),200


@app.route('/tracked-product/<int:product_id>',methods=['PUT'])
def toggle_tracked_product(product_id):
	trck_prd=TrackedProd.query.get(product_id)
	if trck_prd is None:
		response={"message":"Tracked Product not Found"}
		return jsonify(response),404
	trck_prd.tracked=not trck_prd.tracked
	db.session.commit()

	response={"message":"Tracked product toggled successfully"}
	return jsonify(response),200


@app.route('/update-tracked-products',methods=['POST'])
def update_tracked_products():
	trck_prds=TrackedProd.query.all()
	url="https://www.amazon.in"

	prd_names=[]
	for trck_prd in trck_prds:
		name=trck_prd.name
		if not trck_prd.tracked:
			continue
		command = f"python ./Flask/scraper/__init__.py {url} \"{name}\" /results"
		subprocess.Popen(command, shell=True)
		prd_names.append(name)

	response={"message":"Scraper started to update","products":prd_names}
	print(response)
	return jsonify(response),200

if __name__=='__main__':
	with app.app_context():
		db.create_all()
	app.run()





























if __name__=="__main__":
	with app.app_context():
		db.create_all()
	app.run()
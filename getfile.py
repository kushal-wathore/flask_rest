def run(args):
	block_blob_service = BlockBlobService(account_name="asterix", account_key="4Dbtb3ETtxreKbZEHVndMGTNC5JyLnRjLTKHaJeDBjr1fTUENG777GE2OUc3M8x1iLfos1TSd/O70PiADu8psA==")

	url = "https://asterix.blob.core.windows.net/applog/app_test1.zip"
	url = args[1]
	IMAGE_DIR = args[2]

	blob_list = list(block_blob_service.list_blobs('applog'))

	for image_obj in blob_list:
		image_url = block_blob_service.make_blob_url('applog',str(image_obj.name))
		if image_url == url:
			blob_name = image_obj.name
			save_path=os.path.join(IMAGE_DIR, blob_name)
			break
		

	block_blob_service.get_blob_to_path('applog', blob_name , file_path = save_path)
	
	print("Starting unzip")
	#with zipfile.ZipFile(save_path,"r") as zip_ref:
		#zip_ref.extractall(IMAGE_DIR)
	unzip(save_path,IMAGE_DIR)
	
	print("Downloaded")

def unzip(path,IMAGE_DIR):

	with zipfile.ZipFile(path,"r") as zip_ref:
		zip_ref.extractall(IMAGE_DIR)
	
	return "\""+path+"\" was unzipped successfully."

from azure.storage.blob import BlockBlobService
import sys
import zipfile
import os.path
args = sys.argv
sys.exit(run(args))
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
	zip = zipfile.ZipFile(save_path, 'r')
	destination_name = os.path.join(IMAGE_DIR,blob_name[:blob_name.rfind('.')])
	print(destination_name)
	unzip1(destination_name,zip)
	print("Downloaded")

def unzip(path,IMAGE_DIR):
    	
	with zipfile.ZipFile(path,"r") as zip_ref:
		zip_ref.extractall(IMAGE_DIR)
	
	return "\""+path+"\" was unzipped successfully."
	

def unzip1(path, zip):
    # If the output location does not yet exist, create it
    #
    if not isdir(path):
        os.makedirs(path)

    for each in zip.namelist():

        # Check to see if the item was written to the zip file with an
        # archive name that includes a parent directory. If it does, create
        # the parent folder in the output workspace and then write the file,
        # otherwise, just write the file to the workspace.
        #
        if not each.endswith('/'):
            root, name = split(each)
            directory = normpath(join(path, root))
            if not isdir(directory):
                os.makedirs(directory)
            open(join(directory, name), 'wb').write(zip.read(each))



from azure.storage.blob import BlockBlobService
import sys, zipfile, os
from os.path import isdir, join, normpath, split
args = sys.argv
sys.exit(run(args))
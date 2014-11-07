import os
import sys

from . import config
from . import noark5tordf
import shutil


def test_load_config():
    env = {"SESAM_CONF" : "./noark5tordf/"}

    cfg = config.readConfig(os.getcwd() +"/noark5tordf/config/noark5.yaml", logfile="output.log", loglevel="DEBUG", env=env, logger=None)

    assert cfg is not None
    assert 'type_prefix' in cfg
    assert 'subject_prefix' in cfg
    assert 'document_url_prefix' in cfg
    assert 'ObjectElements' in cfg
    assert 'korrespondansepart' in cfg["ObjectElements"]
    assert 'id' not in cfg["ObjectElements"]['korrespondansepart']
    assert 'id-expression' in cfg["ObjectElements"]['korrespondansepart']
    assert 'referanseDokumentfil' in cfg["ObjectElements"]
    assert 'id' not in cfg["ObjectElements"]['referanseDokumentfil']
    assert 'ids' in cfg
    assert 'input_dir' in cfg
    assert 'output_dir' in cfg
    assert 'backup_dir' in cfg
    assert 'logfile' in cfg
    assert 'loglevel' in cfg

    assert cfg["type_prefix"] == "http://www.arkivverket.no/standarder/noark5/arkivstruktur/"
    assert cfg["document_url_prefix"] == "http://localhost:8080/someservice/"
    assert cfg["subject_prefix"] == "http://sesam.io/sys1/"
    assert cfg["ObjectElements"]["korrespondansepart"]["id-expression"] == 'result = randomID()\n'
    assert cfg["ObjectElements"]["referanseDokumentfil"]["value"] == 'result = config["document_url_prefix"] + value\n'
    assert cfg["ObjectElements"]["referanseDokumentfil"]["literal"] == False
    assert len(cfg["ids"]) == 2
    assert "systemID" in cfg["ids"]
    assert "arkivskaperID" in cfg["ids"]
    
    assert cfg["input_dir"] ==  os.path.join(os.getcwd(),"input")
    assert cfg["backup_dir"] == os.path.join(os.getcwd(),"backup")
    assert cfg["output_dir"] == os.path.join(os.getcwd(),"output")
    assert cfg["logfile"] == os.path.join(os.getcwd(),"output.log")
    assert cfg["loglevel"] == "DEBUG"

    assert os.path.isdir("./input")
    assert os.path.isdir("./backup")
    assert os.path.isdir("./output")

    cfg = config.readConfig(os.getcwd() +"/xmltordf/config/noark5.yaml", output_dir="foo", input_dir="bar", backup_dir="zoo", logfile="output.log", loglevel="DEBUG", env=env, logger=None)

    assert cfg is not None
    assert cfg["input_dir"] == os.path.join(os.getcwd(),"bar")
    assert cfg["backup_dir"] == os.path.join(os.getcwd(),"zoo")
    assert cfg["output_dir"] == os.path.join(os.getcwd(),"foo")
 
    assert os.path.isdir("./foo")
    assert os.path.isdir("./bar")
    assert os.path.isdir("./zoo")
   

def test_convert():
    env = {"SESAM_CONF" : "./noark5tordf/"}

    cfg = config.readConfig(os.getcwd() +"/noark5tordf/config/noark5.yaml", "output.log", "DEBUG", env=env, logger=None)
    
    noark5tordf.process_xml_file(cfg,  os.getcwd() + "/noark5tordf/sample/arkivstruktur.xml")

    currdir = os.getcwd()
    
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys1ba2f34cb-dac7-4987-b25c-16bd760a9035-arkiv.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys1c3b4aeec-3369-40fa-a28d-ebc4d7df5190-dokumentbeskrivelse.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys1d2f6dc67-790b-46dd-ad5c-63faff512e0a-journalpost.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys1d5d0a713-aa25-442c-ab89-ba7706395488-journalpost.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys1df8f51dd-754e-4725-adeb-bb5c8b8ffe30-mappe.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys10a141d1e-e095-4bf5-8e4f-c44eb3e714c1-dokumentbeskrivelse.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys10fdfc0db-0fb5-4b7e-8470-baace6f41dbd-dokumentbeskrivelse.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys11a0158a6-fea6-4c4d-950f-a681e2762b9b-journalpost.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys12bac1d95-6907-443b-a9f3-a57f4a7717ac-saksmappe.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys13e6476f3-39c8-4b02-8f4a-7adc775e7c70-dokumentbeskrivelse.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys13f79d8ca-77f0-4dd1-a354-4686b54c4498-dokumentbeskrivelse.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys15e93f9df-9900-4483-9a7f-ea427213caf1-dokumentbeskrivelse.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys18aac37cd-a5d1-4140-8699-1dae3db79c10-journalpost.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys19be74d77-1dc0-424d-ae15-5e5f6c034c7f-mappe.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys100e69f9d-e115-4134-a483-1807cf3e8ff3-mappe.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys1393dbd12-e291-4276-aef8-0b4ba9a022ff-journalpost.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys18689c066-36e3-48be-8bb4-ec535d4a5ece-journalpost.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys1585231e2-9df9-4e2c-8288-2fdba64736c3-arkivdel.nt")
    assert os.path.isfile(currdir + "/output/bhttpsesamiosys1997506499-arkivskaper.nt")

    with open(currdir + "/output/bhttpsesamiosys1c3b4aeec-3369-40fa-a28d-ebc4d7df5190-dokumentbeskrivelse.nt", "r") as infile:
        data = infile.read()
        
        assert data.find('<http://sesam.io/sys1/c3b4aeec-3369-40fa-a28d-ebc4d7df5190> <http://www.arkivverket.no/standarder/noark5/arkivstruktur/journalpost> <http://sesam.io/sys1/8aac37cd-a5d1-4140-8699-1dae3db79c10>.') > -1
        assert data.find('_:dokumentobjekt-10 <http://www.arkivverket.no/standarder/noark5/arkivstruktur/opprettetAv> "Birger Ballangrud (baladmin)".') > -1
        assert data.find('_:dokumentobjekt-12 <http://www.arkivverket.no/standarder/noark5/arkivstruktur/referanseDokumentfil> <http://localhost:8080/someservice/dokumenter/fasit/Avlevering_Kassasjon/Personer/30A00/7a5e0d2d-240f-496d-9671-0efaab16f6d0/9cc95dab-f344-40f2-9243-ca9c92f79e75/29265a60-8c80-4071-b6de-bc22411e9b79/24084cab-aae7-41fe-9a7a-a12d90adda49.pdf>') > -1


if __name__ == '__main__':
    test_load_config()
    test_convert()

"""Immutable compact-shard destinations. Only verified new scratch is removed."""
import base64
import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path
from common import sha


def make_archive(directory,target,manifest):
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
        for name in sorted(manifest):archive.write(Path(directory)/name,name)
        archive.writestr('MANIFEST.json',json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n')
    with zipfile.ZipFile(target) as archive:
        for name,item in manifest.items():
            digest=hashlib.sha256();size=0
            with archive.open(name) as handle:
                for block in iter(lambda:handle.read(1024*1024),b''):digest.update(block);size+=len(block)
            if digest.hexdigest()!=item['sha256'] or size!=item['bytes']:raise ValueError('Archive verification failed')
        if json.loads(archive.read('MANIFEST.json'))!=manifest:raise ValueError('Archive manifest mismatch')
    return {'sha256':sha(target),'bytes':Path(target).stat().st_size}


def s3_client(settings):
    import boto3
    from botocore.config import Config
    profile=settings.get('aws_profile')
    session=boto3.Session(profile_name=profile) if profile else boto3.Session()
    return session.client('s3',region_name=settings.get('region','us-east-1'),config=Config(retries={'mode':'standard','max_attempts':5}))


def persist_archive(path,settings,design_hash,job_id,client=None):
    path=Path(path);digest=sha(path);size=path.stat().st_size
    if settings['kind']=='filesystem':
        destination=Path(settings['root'])/'shards'/design_hash/f'{job_id}-{digest}.zip'
        destination.parent.mkdir(parents=True,exist_ok=True)
        if not destination.exists():
            with destination.open('xb') as out,path.open('rb') as source:shutil.copyfileobj(source,out)
        if destination.stat().st_size!=size or sha(destination)!=digest:raise ValueError('Destination checksum mismatch; scratch preserved')
        return {'kind':'filesystem','path':str(destination),'bytes':size,'sha256':digest,'verified':True}
    if settings['kind']!='s3':raise ValueError('Archive storage requires filesystem or S3')
    client=client or s3_client(settings);bucket=settings['bucket']
    key=f"{settings['prefix'].strip('/')}/{design_hash}/{job_id}-{digest}.zip"
    checksum=base64.b64encode(bytes.fromhex(digest)).decode()
    with path.open('rb') as handle:
        try:
            client.put_object(Bucket=bucket,Key=key,Body=handle,ContentLength=size,ChecksumSHA256=checksum,
                              Metadata={'sha256':digest,'job-id':job_id},IfNoneMatch='*')
        except Exception as error:
            if getattr(error,'response',{}).get('Error',{}).get('Code') not in ('PreconditionFailed','412'):raise
    head=client.head_object(Bucket=bucket,Key=key,ChecksumMode='ENABLED')
    if head['ContentLength']!=size or head.get('ChecksumSHA256')!=checksum or head.get('Metadata',{}).get('sha256')!=digest:
        raise ValueError('S3 checksum not confirmed; scratch preserved')
    return {'kind':'s3','bucket':bucket,'key':key,'bytes':size,'sha256':digest,'checksum_sha256':checksum,'verified':True}


def check_destination(receipt,settings,client=None):
    if receipt['kind']=='filesystem':
        path=Path(receipt['path'])
        if path.stat().st_size!=receipt['bytes'] or sha(path)!=receipt['sha256']:raise ValueError('Changed archived shard')
    elif receipt['kind']=='s3':
        client=client or s3_client(settings)
        head=client.head_object(Bucket=receipt['bucket'],Key=receipt['key'],ChecksumMode='ENABLED')
        if head['ContentLength']!=receipt['bytes'] or head.get('ChecksumSHA256')!=receipt['checksum_sha256']:raise ValueError('Changed remote shard')

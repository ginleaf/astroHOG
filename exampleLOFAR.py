# This file is part of AstroHOG
#
# Copyright (C) 2013-2017 Juan Diego Soler

import sys
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt

sys.path.append('/Users/jsoler/Documents/astrohog/')
from astrohog import *

from astropy.wcs import WCS
from reproject import reproject_interp

def astroHOGexampleLOFAR(frame, vmin, vmax, ksz=1):
	fstr="%4.2f" % frame

	dir='3C196/'
	hdu1=fits.open(dir+'3C196_LOFAR_RMcube_10.fits')
	hdu2=fits.open(dir+'3C196fwhm5_logNHmap.fits')
	hdu3=fits.open(dir+'3C196fwhm10_Qmap.fits')
	hdu4=fits.open(dir+'3C196fwhm10_Umap.fits')

	Qmap=hdu3[0].data
	Umap=hdu4[0].data
	psi=0.5*np.arctan2(-Umap, Qmap)
	ex=np.sin(psi)
	ey=np.cos(psi)

	RMcube=hdu1[0].data

	v1=vmin*1000.;	v2=vmax*1000.
        v1str="%4.1f" % vmin     
	v2str="%4.1f" % vmax
	limsv=np.array([v1, v2, v1, v2])

	sz1=np.shape(hdu1[0].data)
	CTYPE3=hdu1[0].header['CTYPE3']
	CDELT3=hdu1[0].header['CDELT3']
	CRVAL3=hdu1[0].header['CRVAL3']
	CRPIX3=hdu1[0].header['CRPIX3']
	zmin1=0        #int(CRPIX3+(v1-CRVAL3)/CDELT3)
	zmax1=sz1[0]-1  #int(CRPIX3+(v2-CRVAL3)/CDELT3)
	velvec1=hdu1[0].header['CRVAL3']+np.arange(sz1[0])*hdu1[0].header['CDELT3']   #np.arange(v1,v2,CDELT3)/1000.
        
	refhdr=hdu1[0].header.copy()
        NAXIS3=refhdr['NAXIS3']
	del refhdr['NAXIS3']
        del refhdr['CTYPE3']
	del refhdr['CRVAL3']
	del refhdr['CRPIX3']
	del refhdr['CDELT3']
	del refhdr['CUNIT3']
        refhdr['NAXIS']=2

	sz2=np.shape(hdu2[0].data)
	galRMcube=np.zeros([NAXIS3, sz2[0], sz2[1]])		

	for i in range(0, NAXIS3):
		hduX=fits.PrimaryHDU(RMcube[i,:,:]); hduX.header=refhdr
		mapX, footprintX=reproject_interp(hduX, hdu2[0].header)

		galRMcube[i,:,:]=mapX

	# ==========================================================================================================
	sz1=np.shape(galRMcube)
	#x=np.sort(galRMcube.ravel())
  	#minrm=x[int(0.2*np.size(x))]
	minrm=np.std(galRMcube[0,:,:])
	mask1=np.zeros(sz1)
	mask1[(galRMcube > minrm).nonzero()]=1

	mask2=np.zeros(sz2)+1.
	#mask2[:,ymin:ymax,:]=1
        #mask2[(hdu2[0].data < 0.0).nonzero()]=0

	#corrplane=HOGcorr_cube(hdu1[0].data, hdu2[0].data, zmin1, zmax1, zmin2, zmax2, ksz=5)
	#corrplane=HOGcorr_cube(hdu1[0].data, hdu2[0].data, zmin1, zmax1, zmin2, zmax2, ksz=5, mask1=mask1)

	#corrplane=HOGcorr_cube(hdu1[0].data, hdu2[0].data, zmin1, zmax1, zmin2, zmax2, mask1=mask1, mask2=mask2)
	corrplane, corrcube=HOGcorr_cube(galRMcube, np.array([hdu2[0].data]), zmin1, zmax1, 0, 0, ksz=ksz, mask1=mask1, mask2=mask2)
	#corrplane=HOGcorr_cube(hdu1[0].data, hdu2[0].data, zmin1, zmax1, zmin2, zmax2, ksz=5, mask1=mask1, mask2=mask2, wd=3)
	#corrplane=HOGcorr_cube(hdu1[0].data, hdu2[0].data, zmin1, zmax1, zmin2, zmax2, mask1=mask1, mask2=mask2, wd=3)

	#corrplane=HOGcorr_cube(hdu1[0].data, hdu1[0].data, zmin1, zmax1, zmin1, zmax1, mask1=mask1, mask2=mask1)
	#corrplane=HOGcorr_cube(hdu2[0].data, hdu2[0].data, zmin2, zmax2, zmin2, zmax2, mask1=mask2, mask2=mask2)
	
	plt.plot(velvec1, corrplane.ravel())	
	plt.xlabel('RM')
	plt.ylabel('Correlation')
	plt.show()

	#corrvec0, corrcube0=HOGcorr_cubeandpol(galRMcube, ex, ey, zmin1, zmax1, ksz=ksz)
	corrvec1, corrcube1=HOGcorr_cubeandpol(galRMcube, ex, ey, zmin1, zmax1, ksz=ksz, rotatepol=True)

	#plt.plot(velvec1, corrvec0, 'r')
	plt.plot(velvec1, corrvec1, 'b')
        plt.xlabel('RM')
        plt.ylabel('Correlation')
        plt.show()

	import pdb; pdb.set_trace()

	strksz="%i" % ksz

	plt.imshow(corrplane, origin='lower', extent=limsv/1e3)
	plt.xlabel(r'$v_{CO}$ [km/s]')
        plt.ylabel(r'$v_{HI}$ [km/s]')
        plt.yticks(rotation='vertical')
	plt.colorbar()
	plt.savefig('HOGcorrelationPlanck353GRSL'+fstr+'_b'+blimstr+'_k'+strksz+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
        plt.close()
        #import pdb; pdb.set_trace()

def astroHOGexampleHIandPlanck(frame, vmin, vmax, ksz=1):
	fstr="%4.2f" % frame

	dir='/Users/jsoler/PYTHON/HItest/'
        hdu1=fits.open(dir+'lite'+'THOR_and_VGPS_HI_without_continuum_L'+fstr+'_40arcsec.fits')

        dir='/Users/jsoler/PYTHON/HItest/'
        temp=fits.open(dir+'Planck353GHzL'+fstr+'_Qmap.fits')
        Qmap=convolve_fft(temp[0].data,Gaussian2DKernel(3))
        temp=fits.open(dir+'Planck353GHzL'+fstr+'_Umap.fits')
        Umap=convolve_fft(temp[0].data,Gaussian2DKernel(3))
        temp=fits.open(dir+'Planck353GHzL'+fstr+'_LIC.fits')
        LICmap=temp[0].data
        psi=0.5*np.arctan2(-Umap,Qmap)
        Ex=np.sin(psi); Bx=-np.cos(psi)
        Ey=np.cos(psi); By= np.sin(psi)

        v1=vmin*1000.;  v2=vmax*1000.
        v1str="%4.1f" % vmin
        v2str="%4.1f" % vmax
        limsv=np.array([v1, v2, v1, v2])

        CTYPE3=hdu1[0].header['CTYPE3']
        CDELT3=hdu1[0].header['CDELT3']
        CRVAL3=hdu1[0].header['CRVAL3']
        CRPIX3=hdu1[0].header['CRPIX3']
        zmin1=int(CRPIX3+(v1-CRVAL3)/CDELT3)
        zmax1=int(CRPIX3+(v2-CRVAL3)/CDELT3)
        velvec1=CRVAL3+(np.arange(zmin1,zmax1)-CRPIX3)*CDELT3

	lmin1=hdu1[0].header['CRVAL1']-(hdu1[0].header['NAXIS1']-hdu1[0].header['CRPIX1'])*hdu1[0].header['CDELT1']
        lmax1=hdu1[0].header['CRVAL1']+(hdu1[0].header['NAXIS1']-hdu1[0].header['CRPIX1'])*hdu1[0].header['CDELT1']

	sz1=np.shape(hdu1[0].data)

	# ==========================================================================================================
        blim=1.2; blimstr="%2.1f" % blim
        ymax=int(hdu1[0].header['CRPIX2']+( blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        ymin=int(hdu1[0].header['CRPIX2']+(-blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        mask1=np.zeros(sz1)
        mask1[:,ymin:ymax,:]=1
        mask1[(hdu1[0].data < 0.0).nonzero()]=0

	HIcube=hdu1[0].data
        HIcube[(mask1 == 0.).nonzero()]=0.
        HIcube[np.isnan(HIcube).nonzero()]=0.
        lvmap=HIcube[zmin1:zmax1,ymin:ymax,:].sum(axis=1)
        plt.imshow(lvmap, origin='lower', extent=[lmin1,lmax1,vmin,vmax], aspect='auto')
        ax=plt.gca()
        plt.xlabel(r'$l$ [deg]')
        plt.ylabel(r'$v$ [km/s]')
        plt.yticks(rotation='vertical')
        plt.colorbar()
        #plt.show()
	plt.savefig('VLdiagramTHORL'+fstr+'_b'+blimstr+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
        plt.close()

        corrvecA=HOGcorr_cubeandpol(hdu1[0].data, Ex, Ey, zmin1, zmax1, ksz=ksz, mask1=mask1, rotatepol=True)

	# ==========================================================================================================
        blim=0.8; blimstr="%2.1f" % blim
        ymax=int(hdu1[0].header['CRPIX2']+( blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        ymin=int(hdu1[0].header['CRPIX2']+(-blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        mask1=np.zeros(sz1)
        mask1[:,ymin:ymax,:]=1
        mask1[(hdu1[0].data < 0.0).nonzero()]=0

	HIcube=hdu1[0].data
        HIcube[(mask1 == 0.).nonzero()]=0.
        HIcube[np.isnan(HIcube).nonzero()]=0.
        lvmap=HIcube[zmin1:zmax1,ymin:ymax,:].sum(axis=1)
        plt.imshow(lvmap, origin='lower', extent=[lmin1,lmax1,vmin,vmax], aspect='auto')
        ax=plt.gca()
        plt.xlabel(r'$l$ [deg]')
        plt.ylabel(r'$v$ [km/s]')
        plt.yticks(rotation='vertical')
        plt.colorbar()
        #plt.show()
	plt.savefig('VLdiagramTHORL'+fstr+'_b'+blimstr+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
        plt.close()

        corrvecB=HOGcorr_cubeandpol(hdu1[0].data, Ex, Ey, zmin1, zmax1, ksz=ksz, mask1=mask1, rotatepol=True)

	# ===========================================================================================================
        blim=0.4; blimstr="%2.1f" % blim
        ymax=int(hdu1[0].header['CRPIX2']+( blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        ymin=int(hdu1[0].header['CRPIX2']+(-blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        mask1=np.zeros(sz1)
        mask1[:,ymin:ymax,:]=1
        mask1[(hdu1[0].data < 0.0).nonzero()]=0

	HIcube=hdu1[0].data
        HIcube[(mask1 == 0.).nonzero()]=0.
        HIcube[np.isnan(HIcube).nonzero()]=0.
        lvmap=HIcube[zmin1:zmax1,ymin:ymax,:].sum(axis=1)
        plt.imshow(lvmap, origin='lower', extent=[lmin1,lmax1,vmin,vmax], aspect='auto')
        ax=plt.gca()
        plt.xlabel(r'$l$ [deg]')
        plt.ylabel(r'$v$ [km/s]')
        plt.yticks(rotation='vertical')
        plt.colorbar()
        #plt.show()
	plt.savefig('VLdiagramTHORL'+fstr+'_b'+blimstr+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
        plt.close()

        corrvecC=HOGcorr_cubeandpol(hdu1[0].data, Ex, Ey, zmin1, zmax1, ksz=ksz, mask1=mask1, rotatepol=True)

	# =============================================================================================================
        sz2=np.shape(Qmap)
        #testEx=np.random.uniform(low=-1., high=1., size=sz2)
        #testEy=np.random.uniform(low=-1., high=1., size=sz2)
	testEx=np.zeros(sz2)
	testEy=1.+np.zeros(sz2)
        corrvecN=HOGcorr_cubeandpol(hdu1[0].data, testEx, testEy, zmin1, zmax1, ksz=ksz, mask1=mask1, rotatepol=True)

        strksz="%i" % ksz

        plt.plot(velvec1/1e3, corrvecA, 'b', label=r'$|b| <$ 1.2')
        plt.plot(velvec1/1e3, corrvecB, 'g', label=r'$|b| <$ 0.8')
        plt.plot(velvec1/1e3, corrvecC, 'r', label=r'$|b| <$ 0.4')
        plt.plot(velvec1/1e3, corrvecN, 'k')
        plt.ylabel('HOG correlation')
        plt.legend()
        #plt.show()
        plt.savefig('HOGcorrelationPlanck353THORL'+fstr+'_k'+strksz+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
	plt.close()


def astroHOGexampleCOandPlanck(frame, vmin, vmax, ksz=1):
	fstr="%4.2f" % frame

	dir='/Users/jsoler/PYTHON/COtest/'
        hdu1=fits.open(dir+'grs_L'+fstr+'.fits')

	dir='/Users/jsoler/PYTHON/HItest/'
	temp=fits.open(dir+'Planck353GHzL'+fstr+'_Qmap.fits')
        Qmap=convolve_fft(temp[0].data,Gaussian2DKernel(3))
        temp=fits.open(dir+'Planck353GHzL'+fstr+'_Umap.fits')
        Umap=convolve_fft(temp[0].data,Gaussian2DKernel(3))
        temp=fits.open(dir+'Planck353GHzL'+fstr+'_LIC.fits')
        LICmap=temp[0].data
        psi=0.5*np.arctan2(-Umap,Qmap)
        Ex=np.sin(psi); Bx=-np.cos(psi)
        Ey=np.cos(psi); By= np.sin(psi)

        v1=vmin*1000.;  v2=vmax*1000.
        v1str="%4.1f" % vmin
        v2str="%4.1f" % vmax
        limsv=np.array([v1, v2, v1, v2])

        CTYPE3=hdu1[0].header['CTYPE3']
        CDELT3=hdu1[0].header['CDELT3']
        CRVAL3=hdu1[0].header['CRVAL3']
        CRPIX3=hdu1[0].header['CRPIX3']
        zmin1=int(CRPIX3+(v1-CRVAL3)/CDELT3)
        zmax1=int(CRPIX3+(v2-CRVAL3)/CDELT3)
        velvec1=CRVAL3+(np.arange(zmin1,zmax1)-CRPIX3)*CDELT3

	lmin1=hdu1[0].header['CRVAL1']-(hdu1[0].header['NAXIS1']-hdu1[0].header['CRPIX1'])*hdu1[0].header['CDELT1']
	lmax1=hdu1[0].header['CRVAL1']+(hdu1[0].header['NAXIS1']-hdu1[0].header['CRPIX1'])*hdu1[0].header['CDELT1']

        sz1=np.shape(hdu1[0].data)

	# ===========================================================================================================
	blim=1.2; blimstr="%2.1f" % blim
	ymax=int(hdu1[0].header['CRPIX2']+( blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
	ymin=int(hdu1[0].header['CRPIX2']+(-blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        mask1=np.zeros(sz1)
	mask1[:,ymin:ymax,:]=1
        mask1[(hdu1[0].data < 0.0).nonzero()]=0

	COcube=hdu1[0].data
	COcube[(mask1 == 0.).nonzero()]=0.
	COcube[np.isnan(COcube).nonzero()]=0.
	lvmap=COcube[zmin1:zmax1,ymin:ymax,:].sum(axis=1)	
	plt.imshow(lvmap, origin='lower', extent=[lmin1,lmax1,vmin,vmax], aspect='auto')
	ax=plt.gca()
	plt.xlabel(r'$l$ [deg]')
	plt.ylabel(r'$v$ [km/s]')
	plt.yticks(rotation='vertical')
	plt.colorbar()
	#plt.show()
	plt.savefig('VLdiagramGRSL'+fstr+'_b'+blimstr+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
        plt.close()

	corrvecA=HOGcorr_cubeandpol(hdu1[0].data, Ex, Ey, zmin1, zmax1, ksz=ksz, mask1=mask1, rotatepol=True)

	# ===========================================================================================================
	blim=0.8; blimstr="%2.1f" % blim
        ymax=int(hdu1[0].header['CRPIX2']+( blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        ymin=int(hdu1[0].header['CRPIX2']+(-blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        mask1=np.zeros(sz1)
        mask1[:,ymin:ymax,:]=1
        mask1[(hdu1[0].data < 0.0).nonzero()]=0

	COcube=hdu1[0].data
        COcube[(mask1 == 0.).nonzero()]=0.
        COcube[np.isnan(COcube).nonzero()]=0.
        lvmap=COcube[zmin1:zmax1,ymin:ymax,:].sum(axis=1)
        plt.imshow(lvmap, origin='lower', extent=[lmin1,lmax1,vmin,vmax], aspect='auto')
        plt.xlabel(r'$l$ [deg]')
        plt.ylabel(r'$v$ [km/s]')
        plt.yticks(rotation='vertical')
        plt.colorbar()
        #plt.show()
	plt.savefig('VLdiagramGRSL'+fstr+'_b'+blimstr+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
        plt.close()

        corrvecB=HOGcorr_cubeandpol(hdu1[0].data, Ex, Ey, zmin1, zmax1, ksz=ksz, mask1=mask1, rotatepol=True)

	# ===========================================================================================================	
	blim=0.4; blimstr="%2.1f" % blim
        ymax=int(hdu1[0].header['CRPIX2']+( blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        ymin=int(hdu1[0].header['CRPIX2']+(-blim-hdu1[0].header['CRVAL2'])/hdu1[0].header['CDELT2'])
        mask1=np.zeros(sz1)
        mask1[:,ymin:ymax,:]=1
        mask1[(hdu1[0].data < 0.0).nonzero()]=0

	COcube=hdu1[0].data
        COcube[(mask1 == 0.).nonzero()]=0.
        COcube[np.isnan(COcube).nonzero()]=0.
        lvmap=COcube[zmin1:zmax1,ymin:ymax,:].sum(axis=1) 
        plt.imshow(lvmap, origin='lower', extent=[lmin1,lmax1,vmin,vmax], aspect='auto')
        plt.xlabel(r'$l$ [deg]')
        plt.ylabel(r'$v$ [km/s]')
        plt.yticks(rotation='vertical')
	plt.colorbar()
	#plt.show()
	plt.savefig('VLdiagramGRSL'+fstr+'_b'+blimstr+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
        plt.close()

        corrvecC=HOGcorr_cubeandpol(hdu1[0].data, Ex, Ey, zmin1, zmax1, ksz=ksz, mask1=mask1, rotatepol=True)

	# ==============================================================================================================
	sz2=np.shape(Qmap)
	testEx=np.zeros(sz2)
        testEy=1.+np.zeros(sz2)
	corrvecN=HOGcorr_cubeandpol(hdu1[0].data, testEx, testEy, zmin1, zmax1, ksz=ksz, mask1=mask1, rotatepol=True)

	# ==============================================================================================================
	strksz="%i" % ksz

	plt.plot(velvec1/1e3, corrvecA, 'b', label=r'$|b| <$ 1.2')
	plt.plot(velvec1/1e3, corrvecB, 'g', label=r'$|b| <$ 0.8')
	plt.plot(velvec1/1e3, corrvecC, 'r', label=r'$|b| <$ 0.4')
	plt.plot(velvec1/1e3, corrvecN, 'k')
	plt.ylabel('HOG correlation')
	plt.legend()
	#plt.show()
	plt.savefig('HOGcorrelationPlanck353GRSL'+fstr+'_k'+strksz+'_v'+v1str+'to'+v2str+'.png', bbox_inches='tight')
	plt.close()	

	#import pdb; pdb.set_trace()

ksz=9
#astroHOGexampleHIandPlanck(23.75, -5., 135., ksz=9)
#astroHOGexampleCOandPlanck(23.75,  -5., 135., ksz=9)
#astroHOGexampleHIandCO(23.75,  -5.,  30., ksz=ksz)
astroHOGexampleLOFAR(23.75, 100., 135., ksz=ksz)




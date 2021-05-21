#!/usr/bin/python3
# encoding utf-8
# 
# author: Wesley Silva
# https://github.com/xslyrs
#

import requests, base64, subprocess, tempfile, pandas, sys, os, time 

KEY_SOURCE = b'aHR0cDovL3d3dy52cG5nYXRlLm5ldC9hcGkvaXBob25lLw=='

class SlyVPN:
	
	def __init__(self, server=''):
		_datarequest = requests.get(base64.b64decode(KEY_SOURCE).decode()).text.replace('\r','')
		_datalist = [line.split(',') for line in _datarequest.split('\n')]
		_datalist.pop(0)
		_dataheaders = _datalist.pop(0)
		self._datasource = pandas.DataFrame(_datalist, columns=_dataheaders)
		self._datasource = self._datasource.dropna()
		self._datasource['Score'] = self._datasource['Score'].astype(int)
		self._datasource['Ping'] = self._datasource['Ping'].astype(int)
		self._datasource['Speed'] = self._datasource['Speed'].astype(int)
		self._datasource['NumVpnSessions'] = self._datasource['NumVpnSessions'].astype(int)
		self._datasource['Uptime'] = self._datasource['Uptime'].astype(int)
		self._datasource['TotalUsers'] = self._datasource['TotalUsers'].astype(int)
		self._datasource['TotalTraffic'] = self._datasource['TotalTraffic'].astype(int)
		self.server = server

	
	def __SortServer(self, criteria='NumVpnSessions'):
		criteria_available = ['Speed','NumVpnSessions']
		candidates = self._datasource.loc[self._datasource['CountryShort'].str.lower() == self.server.lower()]
		if criteria == 'Speed':
			self._currentvpn = candidates.sort_values(by=['Speed'], ascending=False).iloc[0,:]
		elif criteria == 'NumVpnSessions':
			self._currentvpn = candidates.sort_values(by='NumVpnSessions', ascending=True).iloc[0,:]
		return True if len(self._currentvpn)>0 else False
		
		
	def __MakeTempFile(self):
		_, vpnconfig = tempfile.mkstemp()
		with open(vpnconfig,'w') as f:
			f.write(base64.b64decode(self._currentvpn[-1]).decode())
			f.write('\nscript-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf')
			f.close()
		return vpnconfig
		
	
	def LoadServers(self):
		self.serversavailable = self._datasource['CountryShort'].unique().copy()


	def Start(self):
		if self.__SortServer():
			vpnconfig = self.__MakeTempFile()
			return subprocess.Popen(['sudo','openvpn','--config',vpnconfig])
		else:
			print('Error starting process openvpn')
			return False
	

if __name__ == "__main__":
	try: 
		try:
			i = SlyVPN(sys.argv[1])
			i.LoadServers()
		except:
			print('\nDefine some Server Available.\n')
			quit()

		if i.server not in i.serversavailable: 
			print('\nCurrently servers available:')
			for srv in i.serversavailable:
				print(f' {srv}')
			print('\n')
			quit()

		connection = i.Start()
		try: 
			while True : time.sleep(666)
		except:
			connection.kill()
		
		while connection.poll()!=0:
			time.sleep(1)

	except Exception as e:
		print( e.message if hasattr(e,'message') else e )
	
	

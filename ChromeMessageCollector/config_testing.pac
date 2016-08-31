function FindProxyForURL(url, host) {
if (shExpMatch(url, "https:*csi.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*encrypted-tbn0.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*encrypted-tbn1.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*encrypted-tbn3.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*news.google.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*ssl.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*t0.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*t1.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*t2.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*t3.gstatic.com*"))	return "DIRECT";
if (shExpMatch(url, "https:*www.google-analytics.com*"))	return "DIRECT";
}
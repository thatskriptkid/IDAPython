/* Код для LINQPAD, чтобы отобразить инфу о x509 сертификате. Также с помощью
этого кода можно проверить валидность сертификата */


void Main()
{
	string fileName = "c:\\my\\OUTLOOK.CFG";
	X509Certificate2 x509 = new X509Certificate2(fileName, "notasecret", X509KeyStorageFlags.Exportable);
	
	Console.WriteLine("{0}Subject: {1}{0}", Environment.NewLine, x509.Subject);
    Console.WriteLine("{0}Issuer: {1}{0}", Environment.NewLine, x509.Issuer);
    Console.WriteLine("{0}Version: {1}{0}", Environment.NewLine, x509.Version);
    Console.WriteLine("{0}Valid Date: {1}{0}", Environment.NewLine, x509.NotBefore);
    Console.WriteLine("{0}Expiry Date: {1}{0}", Environment.NewLine, x509.NotAfter);
    Console.WriteLine("{0}Thumbprint: {1}{0}", Environment.NewLine, x509.Thumbprint);
    Console.WriteLine("{0}Serial Number: {1}{0}", Environment.NewLine, x509.SerialNumber);
    Console.WriteLine("{0}Friendly Name: {1}{0}", Environment.NewLine, x509.PublicKey.Oid.FriendlyName);
    Console.WriteLine("{0}Public Key Format: {1}{0}", Environment.NewLine, x509.PublicKey.EncodedKeyValue.Format(true));
    Console.WriteLine("{0}Raw Data Length: {1}{0}", Environment.NewLine, x509.RawData.Length);
    Console.WriteLine("{0}Certificate to string: {1}{0}", Environment.NewLine, x509.ToString(true));
    Console.WriteLine("{0}Certificate to XML String: {1}{0}", Environment.NewLine, x509.PublicKey.Key.ToXmlString(false));
}
using System;
using System.Drawing;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Text;
using System.Security.Cryptography;

/*
Код взят из образца:
6BE0ECD544888A0DAF58AAD1476A860EBA41A1214CDDD845899EEADD836FE12D

Функция Dec() расшифровывает блоб из base64 строки алгоритмом AES
*/

namespace Outstanding
{
   class Program
   {
       static void Main(string[] args)
       {
           string text = File.ReadAllText(@"b64_blob.bin", Encoding.UTF8);
           byte[] data = Convert.FromBase64String(text);
			byte[] array = Dec(data);
            File.WriteAllBytes("output.bin", array);
       }
       public static byte[] Dec(byte[] data)
		{
			byte[] array = new byte[16];
			byte[] array2 = new byte[16];
			Array.Copy(data, 0, array, 0, 16);
			Array.Copy(data, 16, array2, 0, 16);
			Console.WriteLine(new Guid(array));
			Console.WriteLine(new Guid(array2));
			MemoryStream memoryStream = new MemoryStream();
			CryptoStream cryptoStream = new CryptoStream(memoryStream, new RijndaelManaged
			{
				BlockSize = 128,
				KeySize = 128,
				Mode = CipherMode.CBC,
				Padding = PaddingMode.PKCS7
			}.CreateDecryptor(array2, array), CryptoStreamMode.Write);
			cryptoStream.Write(data, 32, data.Length - 32);
			cryptoStream.FlushFinalBlock();
			return memoryStream.ToArray();
		}
   }
}
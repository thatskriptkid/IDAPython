using System;
using System.Security.Cryptography;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

// Расшифровывает конфигурацию из стеганографических изображений

namespace Outstanding
{
   class Program
   {

        public static byte[] aes_decrypt(byte[] buff) 
        {
            // Ключ надо достать статически из образца, для каждого образца он уникален
            byte[] array2 = new byte[] {0x51, 0x2a, 0x3b, 0x07, 0x1b, 0x46, 0x53, 0x0d, 0x47, 0x4b, 0x11, 0x09, 0x27, 0x40, 0x03, 0x02};
            byte[] result;

            using (RijndaelManaged rijndaelManaged = new RijndaelManaged())
            {
                rijndaelManaged.Key = array2;
                rijndaelManaged.IV = array2;
                rijndaelManaged.Mode = CipherMode.ECB;
                rijndaelManaged.Padding = PaddingMode.ISO10126;
                using (ICryptoTransform cryptoTransform = rijndaelManaged.CreateDecryptor(array2, rijndaelManaged.IV))
                {
                    using (MemoryStream memoryStream = new MemoryStream())
                    {
                        using (CryptoStream cryptoStream = new CryptoStream(memoryStream, cryptoTransform, CryptoStreamMode.Write))
                        {
                        Console.WriteLine(buff.Length);
                            cryptoStream.Write(buff, 0, buff.Length);
                            cryptoStream.FlushFinalBlock();
                            result = memoryStream.ToArray();
                        }
                    }
                }
            }
            return result;
        }
        static void Main(string[] args)
        {
            Image[] img_ar = new Image[14];
            
            // Загружаем ПО ПОРЯДКУ все изображения из ресурсов
            for(int ij = 0;ij < 14;ij++)
            {
                img_ar[ij] = Image.FromFile("D:\\ag\\dump\\imgs\\c33d077f" + ij);
                
            }
            
            MemoryStream memoryStream = new MemoryStream();
            
            foreach(Image image in img_ar) {
                Rectangle rectangle = new Rectangle(Point.Empty, image.Size);
                MemoryStream stream = new MemoryStream();
                image.Save(stream, ImageFormat.Png);
                Bitmap bitmap = new Bitmap(stream);
                BitmapData bitmapData = bitmap.LockBits(rectangle, ImageLockMode.ReadWrite, PixelFormat.Format24bppRgb);
                byte[] array = new byte[Marshal.ReadInt32(bitmapData.Scan0) + 15 - 1 + 1];
                IntPtr scan = bitmapData.Scan0;
                byte[] array2 = array;
                for (int j=0;j<array2.Length; j++) {
                    Marshal.Copy(new IntPtr((int)scan + 6), array, 0, array.Length);
                    
                }
                bitmap.UnlockBits(bitmapData);
                memoryStream.Write(array, 0, array.Length);
            }
            byte[] res = memoryStream.ToArray();
            res = Program.aes_decrypt(res);
            File.WriteAllBytes("D:\\res.bin", res);
        }
   }
}
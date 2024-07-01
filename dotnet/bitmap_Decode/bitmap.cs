// Author:Bauyrzhan.Dyussekeyev

using System;
using System.Drawing;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Text;

namespace Outstanding
{
   class Program
   {
       static void Main(string[] args)
       {
        
            Bitmap bitmap = (Bitmap) Bitmap.FromFile("target.bin");
            //bitmap = preapare_bitmap(bitmap, 150, 150);
            byte[] bitmap_arr = b5(bitmap);
            byte[] bitmap_decoded = decode(bitmap_arr, "jvz");
            //byte[] payload = getPayload(bitmap_decoded);
            File.WriteAllBytes("output.bin", bitmap_decoded);
           
       }
        private static byte[] b5(Bitmap bitmap)
        {
            int num = 0;
            int width = bitmap.Width;
            byte[] array;
            int num5;
            int i = 0;
            int num4 = 0;
            num5 = width * width * 4;
            array = new byte[num5];


            for (;;)
            {
                while (i < width)
                {
                    Array.Copy(BitConverter.GetBytes(bitmap.GetPixel(num4, i).ToArgb()), 0, array, num, 4);
                    num += 4;
                    i++;
                }
                num4++;
                if (num4 >= width)
                {
                    break;
                }
            }
            int num6 = BitConverter.ToInt32(array, 0);
            byte[] array2 = new byte[num6];
            Array.Copy(array, 4, array2, 0, array2.Length);
            return array2;
        }

       private static byte[] bitmapToArray_v2(Bitmap bitmap_0)
		{
			int num = 0;
			int width = bitmap_0.Width;
			byte[] array;
            int num5 = width * width * 4;
            array = new byte[num5];
            int num4 = 0;
            int i = 0;

            while (i < width)
            {
                Array.Copy(BitConverter.GetBytes(bitmap_0.GetPixel(num4, i).ToArgb()), 0, array, num, 4);
                num += 4;
                i++;
            }
			int num6 = BitConverter.ToInt32(array, 0);
			byte[] array2 = new byte[num6];
			Array.Copy(array, 4, array2, 0, array2.Length);
			return array2;
		}

       public static byte[] getPayload(byte[] bitmap_decoded)
       {
           byte[] result;
           using (MemoryStream memoryStream = new MemoryStream(bitmap_decoded))
           {
               byte[] array = new byte[4];
               memoryStream.Read(array, 0, 4);
               int num = BitConverter.ToInt32(array, 0);
               using (GZipStream gzipStream = new GZipStream(memoryStream, CompressionMode.Decompress))
               {
                   byte[] array2 = new byte[num];
                   gzipStream.Read(array2, 0, num);
                   result = array2;
               }
           }
           return result;
       }

       private static byte[] bitmapToArray_v1(Bitmap bitmap_0)
       {
           List<byte> list = new List<byte>();
           checked
           {
               int num = bitmap_0.Width - 1;
               for (int i = 0; i <= num; i++)
               {
                   int num2 = bitmap_0.Height - 1;
                   for (int j = 0; j <= num2; j++)
                   {
                       Color pixel = bitmap_0.GetPixel(i, j);
                       if (pixel != Color.FromArgb(0, 0, 0, 0))
                       {
                           list.InsertRange(list.Count, new byte[]
                           {
                               pixel.R,
                               pixel.G,
                               pixel.B
                           });
                       }
                   }
               }
               return (byte[])list.ToArray();
           }
       }
        
        public static Bitmap preapare_bitmap(Bitmap bitmap_0, int int_0, int int_1)
		{
			int num = bitmap_0.Width - int_0;
			int num2 = bitmap_0.Height - int_1;
			Bitmap bitmap = new Bitmap(num, num2);
			for (int i = 0; i < num2; i++)
			{
				int j = 0;
				while (j < num)
				{
					Color pixel = bitmap_0.GetPixel(j, i);
					bitmap.SetPixel(j, i, pixel);
                    j++;
                    break;
				}
			}
			return bitmap;
		}
       public static byte[] decode(byte[] bitmap_arr, string key)
       {
           byte[] bytes = Encoding.ASCII.GetBytes(key);
           int num = (int)(bitmap_arr[bitmap_arr.Length - 1] ^ 112);
           byte[] array = new byte[bitmap_arr.Length + 1];
           int num2 = 0;
           for (int i = 0; i <= bitmap_arr.Length - 1; i++)
           {
               array[i] = (byte)((int)bitmap_arr[i] ^ num ^ (int)bytes[num2]);
               if (num2 == key.Length - 1)
               {
                   num2 = 0;
               }
               else
               {
                   num2++;
               }
           }
           Array.Resize<byte>(ref array, bitmap_arr.Length - 1);
           return array;
       }
   }
}
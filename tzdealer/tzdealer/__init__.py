def get_lucky_comb(array_numb, amt, comb=2):
   from itertools import combinations 

   main  = array_numb
   inve  = mixed = []
   ppc   = dif = total_c = total_n = left = 0
   for m in main:
      inve.append(m[1]+m[0])

   # Create combinations
   mixed  = list(combinations(main + inve, comb))
   # Let's remove duplicates
   mixed = list(set(mixed))
   print("main: {}\ninve: {}".format(main, inve))
   for idx, m in enumerate(mixed):
      print("{}\t{}".format(idx, m))
   ppc = int(amt/len(mixed))
   dif = amt - (ppc * len(mixed))
   ppn = dif / (len(array_numb) * 2)
   toc = ppc *  len(mixed)
   ton = ppn *  len(array_numb) * 2
   lef = amt - toc - ton
   print("ppc: {} tot: {}".format(ppc, toc))
   print("ppn: {} tot: {}".format(ppn, ton))
   print("lef: {} ".format(lef))
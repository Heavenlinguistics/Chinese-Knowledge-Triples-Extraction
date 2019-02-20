# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 16:15:02 2019

@author: Administrator
"""
def get_indices(li,ele):
    i_word=list(enumerate(li))
    indices=[]
    for tpl in i_word:
        if ele in tpl:
            indices.append(tpl[0])
    return indices
def get_eles(li,indices):
    eles=[]
    for i in indices:
        eles.append(li[i])
    return eles

def have_r_with(words_li,dpd_li,i,r):
    """
   返回和words_li[i]构成关系r的成分以及和这个成分并列的成分的indices
    """
    indices=[]
    tag=str(i+1)+':'+r
    ins=get_indices(dpd_li,tag)
    if r=='COO':
       return  get_indices(dpd_li,tag)
    elif ins!=[]:
        for j in ins:
            coos=[]
            coos.append(j)
            coos.extend(have_r_with(words_li,dpd_li,j,'COO'))    
            indices.append(coos)
    return indices

def get_verbs(words_li,dpd_li,n_i):
     """
    返回与给定名词构成主谓关系的所有动词。注意事先已经确定句中存在一个动词与words_li[n_i]构成主谓关系。
     """
     noun_dpd=dpd_li[n_i]
     verb_is=[]
     #获得一个与给定名词构成‘SBV’关系的动词
     verb_i=int(noun_dpd.split(':')[0])-1
     verb_is.append(verb_i)
     verbs=[]
     verbs=have_r_with(words_li,dpd_li,verb_i,'COO')     
     for v in verbs:
             #如果n和v构成SBV的关系，而且存在某个单词和v的并列词构成SBV的关系
             nouns=have_r_with(words_li,dpd_li,v,'SBV') 
             if nouns!=[] and 'SBV' in noun_dpd:
                 flag=0
                 for n in nouns:
                     for n_or_c in n:
                         if words_li[n_or_c]!=words_li[n_i]:
                             flag=1
                 if flag==1:
                     break
                 else:
                     verb_is.append(v)
             else:
                 verb_is.append(v)                 
     return verb_is

def get_tadvs(words_li,pos_li,j):
    """
    获取时间状语
    """
    d=''
    while pos_li[j]!='p' and j>0:
        d=words_li[j]+d
        j-=1
    d=words_li[j]+d 
    return d

            
def get_dadvs(words_li,pos_li,j):
    """
    获取方位状语
    """
    d=''
    while pos_li[j]!='p' and words_li[j]!='，'and j>0:
          d=words_li[j]+d
          j-=1
    if words_li[j]!='，':
        d=words_li[j]+d 
    return d
                   
                       
def get_phrs(words_li,pos_li,dpd_li,head_i,flag):
    """
    获取在words_li中所有修饰head的成分。
    其中head_i是中心成分在words_li中的index and flag tells that whether the head is a noun or a verb.
    """
    elabs=''
    if flag=='v':
        d=''
        c=''
        advs=have_r_with(words_li,dpd_li,head_i,'ADV')
        cmps=have_r_with(words_li,dpd_li,head_i,'CMP')
        if advs!=[]:
               #获取最外层副词到动词之间的字符串
               k=advs[0][0]
               if '时' in words_li[k]:
                   d=get_tadvs(words_li,pos_li,k)
                   k+=1
               elif pos_li[k]=='nd':
                   d=get_dadvs(words_li,pos_li,k)
                   k+=1
               while k<head_i:
                       d+=words_li[k]
                       k+=1  
        #加上右联助词
        next_=head_i+1
        if pos_li[next_]=='u' and words_li[next_]!='的':
            c+=words_li[next_]
        #添加上补语修饰成分
        for cmp in cmps:
              c+=''.join(get_eles(words_li,cmp))
        phrs=d+words_li[head_i]+c 
    #如果中心词是名词的话
    else:
        atts=have_r_with(words_li,dpd_li,head_i,'ATT')
        if atts==[]:
            return ('',words_li[head_i])
        for att in atts:
            #将名词修饰成分右边的助词也作为修饰成分的一部分
            elabs+=get_phrs(words_li,pos_li,dpd_li,att[0],'n')[0]+words_li[att[0]]
            #对该修饰成分的并列成分进行处理：如果最后一位修饰成分的后面存在助词‘的’，那么截取至‘的’；如果‘的’不存在，则截取至最后一个修饰成分即可
            if len(att)>1:
                k=att[-1]+1
                coos=''
                while words_li[k]!='的' and pos_li[k]!='wp':
                    k+=1
                if words_li[k]=='的':
                    coos=''.join(words_li[att[0]+1:k+1])
                else:
                    coos=''.join(words_li[att[0]+1:att[-1]+1])
                elabs+=coos
            if 'RAD' in dpd_li[att[0]+1]:
                elabs+=words_li[att[0]+1]
        phrs=elabs+words_li[head_i]
    return elabs,phrs

def get_noun_r(words_li,pos_li,dpd_li,n_i,v_i):
    """
    获取一个给定了index的名词的修饰关系
    """
    elaborate=''
    s=''
    after=words_li[n_i+1] 
    if  '的'==after:
        j=n_i+2
    else:
        j=n_i+1
    #给定名词修饰其后的名词
    while pos_li[j]=='n':
        elaborate+=words_li[j]
        j+=1
    if  '的'==after:
        i=v_i
        while i<=n_i:
            s+=words_li[i]
            i+=1
        #给定名词参与其后名词的修饰
        #如果'的'在后，有可能给定名词和给定动词构成一套动宾修饰‘的’后面的名词；也有可能给定动词其实应该直接修饰‘的’后面的名词，而给定名词只是‘的’后面的名词的修饰成分。
        s+='的'+elaborate
        return s
    return elaborate
            
            
def get_pure_r(words_li,dpd_li,dops,sps,r):
    """
    去除relation中的主语和宾语。其中o_is和s_is分别是宾语和主语在句中的indices
    """
    for dop in dops:
        r=r.replace(dop,'')
    for sp in sps:
        r=r.replace(sp,'')
    return r
        
def get_objects(words_li,pos_li,dpd_li,verb_i):
    """
    获取某个动词的直接宾语和间接宾语
    """
    iops=[]
    dops=[]
    do=''
    #获取间接宾语，通常有间接宾语一定有直接宾语。假定给定动词只有一组间接宾语。
    li1=have_r_with(words_li,dpd_li,verb_i,'IOB')
    for o in li1:
        io=get_phrs(words_li,pos_li,dpd_li,o[0],'n')[1]
        i=o[-1]
        if len(o)>1:
            io+=''.join(words_li[o[0]+1:i+1])
            print(io)
        iops.append(io)    
        #获取“告诉”的直接宾语  
        if words_li[verb_i]=='告诉':
            if words_li[i+1]=='，':
                k=i+2
            else:
                k=i+1
            while 'WP' not in dpd_li[k]:
                do+=words_li[k]
                k+=1 
            dops.append(do)
            return iops,dops
    #如果动词是非间宾动词或者它是间宾动词但该动词不是“告诉”
    else:
        li2=have_r_with(words_li,dpd_li,verb_i,'VOB')
        for d in li2:
            do=get_phrs(words_li,pos_li,dpd_li,d[0],'n')[1]
            if len(d)>1:
                do+=''.join(words_li[d[0]+1:d[-1]+1])
            dops.append(do)
        return iops,dops      
             
def delete_items(li,val):
    """
    删除列表中所有值等于val的元素。
    """
    while val in li:
        li.remove(val)
    return li

def get_keywords(words_li,dpd_li,n_i,v_i):
    """
    获取新的关键词。
    """
    keywords=[]
    ns_ins=have_r_with(words_li,dpd_li,v_i,'SBV')
    no_ins=have_r_with(words_li,dpd_li,v_i,'VOB')
    for s in ns_ins:
        keywords.extend(get_eles(words_li,s))
    for o in no_ins:
        keywords.extend(get_eles(words_li,o))
    keywords=list(set(keywords))
    return keywords

def find_a_sent():
    fo1=open('new_words.txt','r',encoding='utf-8')
    lines1=fo1.readlines()
    fo2=open('new_pos.txt','r',encoding='utf-8')
    lines2=fo2.readlines()          
    fo3=open('new_dependencies.txt','r',encoding='utf-8')  
    lines3=fo3.readlines()  
    fo4=open('dictionary.txt','r',encoding='utf-8')
    lines4=fo4.readlines()
    nouns=[]
    for line in lines4:
        nouns.append(line.strip())
    nouns=list(set(nouns))
    for i in range(len(lines1)):  
        if 'COO' in lines3[i] and 'v' in lines2[i]:
            print(lines3[i])
            print (lines1[i])
            
def get_triples(words,pos,dpds,nouns,trpl_f,r_f):
    fw=open(trpl_f,'w',encoding='utf-8')
    fw2=open(r_f,'w',encoding='utf-8')
    r=len(words)
    dictionary=[]
    ins_to_delete=[]
    for i in range(r):
        #get the words list and the dependencies list
        words_li=words[i].strip().split()
        dpd_li=dpds[i].strip().split()
        pos_li=pos[i].strip().split()
        for noun in nouns:
            noun_indices=get_indices(words_li,noun)
            #if  the noun appears in the sentence
            if noun_indices!=[]:
                #for each token of the noun in the sentence
                for j in noun_indices:
                    if '的'!=words_li[j+1]:
                        #获得noun 修饰限定其他名词这样的三元组
                        elaborate=get_noun_r(words_li,pos_li,dpd_li,j,0)
                        if elaborate!='':
                            noun=words_li[j]
                            fw.write(noun+'  修饰限定  '+elaborate+'\n')
                            fw2.write(noun+elaborate+'\n')
                    verb_is=[]
                    noun_dpd=dpd_li[j]
                    if 'SBV' in noun_dpd:
                        verb_is=get_verbs(words_li,dpd_li,j)
                        ins_to_delete.append(i)
                    elif 'VOB' in noun_dpd:
                        m=int(noun_dpd.split(':')[0])-1
                        verb_is.append(m)
                        ins_to_delete.append(i)
                    else:
                        break
                    if verb_is!=[]:
                        noun_li=[]
                        noun_li.append(j)
                        noun_li.extend(have_r_with(words_li,dpd_li,j,'COO'))
                    for verb_i in verb_is: 
                        #获取与给定名词构成主谓或者动宾关系的动词的直接宾语和间接宾语
                        iops,dops=get_objects(words_li,pos_li,dpd_li,verb_i)
                        #获取该动词的主语
                        subjects=have_r_with(words_li,dpd_li,verb_i,'SBV')
                        s_is=[]
                        for ss in subjects:
                                 s=get_phrs(words_li,pos_li,dpd_li,ss[0],'n')[1]
                                 if len(ss)>1:
                                     s+=''.join(words_li[ss[0]+1:ss[-1]+1])
                                 s_is.append(s)
                        #获取关系
                        relation=get_phrs(words_li,pos_li,dpd_li,verb_i,'v')[1]
                        relation=get_pure_r(words_li,dpd_li,dops,s_is,relation)
                        #写入三元组
                        if iops==[]:
                            iops=['null']
                        if dops==[]:
                            dops=['null']
                        if s_is==[]:
                            s_is=['null']
                        for sb in s_is:
                            for iop in iops:
                                for dop in dops:
                                    fw.write(sb+' '+relation+' '+iop+' '+dop+'\n')
                                    fw2.write(relation+'\n')
                        #获取新一轮的关键词           
                        dictionary.extend(get_keywords(words_li,dpd_li,j,verb_i)) 
    fw.close()   
    dictionary=set(dictionary)
    nouns=set(nouns)
    #获得新一轮的关键词，这些关键词必须不与上一轮的关键词重合
    dictionary=dictionary-(dictionary&nouns)
    for ele in set(ins_to_delete):
        words[ele]=''
        pos[ele]=''
        dpds[ele]=''
    words=delete_items(words,'')
    pos=delete_items(pos,'')
    dpds=delete_items(dpds,'') 
    return (words,pos,dpds,dictionary)       


def bootstrap(words_f,dpds_f,dict_f):
    fo1=open(words_f,'r',encoding='utf-8')
    words=fo1.readlines()
    fo2=open(dpds_f,'r',encoding='utf-8')
    dpds=fo2.readlines()
    fo3=open(dict_f,'r',encoding='utf-8')
    dictionary=fo3.readlines()
    nouns=[]
    for noun in dictionary:
        nouns.append(noun.strip())
    nouns=list(set(nouns))
    fo4=open('new_pos.txt','r',encoding='utf-8')
    pos=fo4.readlines()
    i=0
    while len(words)>0 and len(nouns)>0:
        trpl_f='triples'+str(i)+'.txt'
        r_f='relations'+str(i)+'.txt'
        results=get_triples(words,pos,dpds,nouns,trpl_f,r_f)
        words=results[0]
        pos=results[1]
        dpds=results[2]
        nouns=results[3]
        i+=1
      




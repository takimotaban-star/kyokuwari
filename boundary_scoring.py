import copy

def score(candidates):
    for i in range(len(candidates)):
      candidates[i]['boundary_score'] = 0 
      candidates[i]['confidence'] = '' 
      candidates[i]['score_details'] = {} 
    
    return candidates

def score_absolute(candidates,length):
  split_count = length/240
  global absolute_point
  absolute_point = []
  j=1
  for i in range(1,round(split_count)+1):
      j += 1
      i *= 240
      if i >= length :
        absolute_point.append({'end':length})
        break
      else:  
        absolute_point.append(i)
        if j == round(split_count)+1:
           absolute_point.append({'end':length})
  for judge in candidates:
    for i in range(len(absolute_point)):
      if type(absolute_point[i]) != dict:
        try:
          point = max(-1,4-1.02337387**(abs(judge['position']-absolute_point[i])))
        except OverflowError as err:
          return None , err
        if abs(judge['position']-absolute_point[i]) <=70:
          judge['boundary_score'] += point
          judge['score_details']['absolute_score'] = point
          break
        
  return candidates , 0
    
def score_relative(candidates,lenght):
  global relative_point
  relative_point = []
  if len(candidates) == 1:
    relative_point.append(240)
    relative_point.append({'end':lenght})
    if 180 <= candidates[0]['position'] <= 300:
      candidates[0]['boundary_score'] += 4
      candidates[0]['score_details']['relative socore'] = 4
  else:
    for i,one_list in enumerate(candidates):

      if i == 0:
        relative_point.append(240)
        relative_point.append(one_list['position']+240)
        try:
          point = max(-2,5-1.01622458**(abs(one_list['position']-240)))
          one_list['boundary_score'] += point
          one_list['score_details']['relative socore'] = point
          point = max(-2,5-1.01622458**(abs(one_list['position']+240-candidates[1]['position'])))
        except OverflowError as err:
          return None,err
        candidates[1]['boundary_score'] += point
        candidates[1]['score_details']['relative socore'] = point

      elif i == len(candidates)-1:
        relative_point.append({'end':lenght})
        break
      else:
        relative_point.append(one_list['position']+240)
        try:
          point = max(-2,5-1.01622458**(abs(one_list['position']+240-candidates[i+1]['position'])))
        except OverflowError as err:
          return None,err
        candidates[i+1]['boundary_score'] += point
        candidates[i+1]['score_details']['relative socore'] = point

  return candidates,0

storage = []
def filter_nearby(candidates):
  global storage
  storage = []
  start_filter_number = []
  for i,one_list in enumerate(candidates):
    if one_list['position'] <= 120:
      start_filter_number.append(i)

  for del_point in sorted(start_filter_number,reverse=True):
    storage.append(copy.deepcopy(candidates[del_point]))
    candidates.pop(del_point)


  for i,one_list in enumerate(candidates):
    del_position = []
    for j in range(i+1,len(candidates)):
      if one_list['position'] <= candidates[j]['position'] <= one_list['position'] +10:
        del_position.append(j)
    for del_point in sorted(del_position,reverse=True):
      storage.append(copy.deepcopy(candidates[del_point]))
      candidates.pop(del_point)
  
  if len(storage) != 0:
    storage.sort(key=lambda c: c['position'])

  return candidates

def score_silence(candidates):
  for interval_score in candidates:
    try:
      add = min(1.1*(2**interval_score['duration'])-1,3)
    except OverflowError as err:
      return None , err
    interval_score['boundary_score'] += add
    interval_score['score_details']['silence'] = add
  return candidates , 0

def detect_diviation(candidates):
  global absolute_point
  global relative_point
  absolute_point[:-1] = sorted(absolute_point[:-1])
  relative_point[:-1] = sorted(relative_point[:-1])

  for i,relative in enumerate(relative_point):
    if type(relative) != dict:
      buffer = []
      for absolute in absolute_point:
        if type(absolute) != dict:
          buffer.append(abs(relative-absolute))
      if not buffer:
          continue
      buffer.sort()
      delta_t = buffer[0]
      if delta_t > 60:
        t = delta_t - 60
        point = min(0.015*t*(1.015**t),3)
        candidates[i]['boundary_score'] -= point
        candidates[i]['score_details']['diviation'] = -point

  return candidates

def classify_conf(candidates):
    for one_list in candidates:
      if one_list['boundary_score'] >=6:
        one_list['confidence'] =2
      elif 6 > one_list['boundary_score'] >=3:
        one_list['confidence'] = 1
      else:
         one_list['confidence'] = 0
    return candidates

shibakari_storage = []
def shibakari(candidates):
  global shibakari_storage
  shibakari_storage = []
  buffer = []
  for i,one_list in enumerate(candidates):
    if one_list['confidence'] == 0:
      buffer.append(i)
      shibakari_storage.append({'list_number':i,'list':one_list})
  buffer.sort(reverse=True)
  for i in buffer:
    candidates.pop(i)

  return candidates
  
# 考生/家长常问问题清洗结果

共清洗出 152 条问题。`question_colloquial_clean` 保留口语风格，`question_normalized` 用于检索/function-call 测试。

## 问题类型分布
- rank_to_school_match: 36
- major_profile: 34
- employment_summary: 19
- school_major_profile: 19
- comparison_query: 16
- transfer_policy_lookup: 11
- rank_to_major_match: 6
- major_market_reference: 4
- score_to_rank: 3
- subject_requirement_lookup: 3
- civil_service_role_search: 1

## 分类型样例

### rank_to_school_match

- 问法：所以说如果也是可以学计算机的,可以没问题。550分,麻烦老师能推荐一下学校吗?有没有您觉得比较合适的?
  标准化：550分计算机专业学校推荐？
  预期工具：rank_to_school_match, major_profile；缺槽：省份, 位次；质量：B
- 问法：上不了本科,想报专科。专科怎么选专业啊?想问一下哪个更好。专科的几个选择首先第一,如果你能接受医学的话,尽量报口腔。如果你比本科线高个三四十分报一个专科的口腔,就业都不会差吧?
  标准化：比本科线高三四十分,报专科口腔医学好吗？
  预期工具：major_lookup, rank_to_school_match；缺槽：province, exact_score；质量：B
- 问法：你5000位能上哪些学校?
  标准化：位次5000可以报考哪些学校？
  预期工具：rank_to_school_match；缺槽：省份, 年份, 科类；质量：B
- 问法：文棋儿怎么报
  标准化：文棋儿如何填报志愿？
  预期工具：school_major_profile, transfer_policy_lookup；缺槽：score, rank, province；质量：B
- 问法：你科学生三万名怎么报？
  标准化：理科生三万名如何填报志愿？
  预期工具：rank_to_school_match, rank_to_major_match；缺槽：省份, 年份；质量：B

### major_profile

- 问法：他对计算机比较感兴趣,但专科学计算机要不要学啊?然后后面再升学,可以学没有问题,然后生本吗?
  标准化：专科计算机专业,毕业后能否升学？
  预期工具：major_lookup, school_lookup；缺槽：province, exact_score, direction；质量：B
- 问法：那就像那一本科就只有一个批次了,是吧?是的。好的,谢谢张老师,另外还有一个问题,我想问一下孩子他说他想学区块链这个专业,我就不太懂这一块。
  标准化：区块链专业属于哪个学科门类？
  预期工具：major_profile, major_lookup；缺槽：score, province, region；质量：B
- 问法：不过你家里有点的话可以报，你家里没点的话就别报。她那个是很吃资源的，这个专业你即使是名校你也吃资源，真的。来我们干金融的朋友啊，说对不对。这个专业即使你是名校你也要吃资源，知道吧。金融这个专业我这么跟你说家长，名校里面很多人是什么，她是已经有工作，带着工作去学金融的知道吗？有的孩子是带着工作去学金融的。
  标准化：金融专业在没有家庭资源的情况下是否值得报考？
  预期工具：major_profile, major_market_reference；缺槽：specific_score, specific_province, specific_school；质量：B
- 问法：说一说，就想问问我姑娘以后报志愿的时候怎么查专业。我们是普通家庭，我姑娘能考635分。你到时候想挑什么？
  标准化：我女儿高考635分，能报什么专业？
  预期工具：major_profile, school_lookup；缺槽：无；质量：B
- 问法：孩子，不带物理的专业，你去送学怎么样？
  标准化：有哪些不需要物理的专业可以推荐？
  预期工具：major_lookup, major_market_reference, employment_summary；缺槽：省份, 分数, 科目组合；质量：B

### employment_summary

- 问法：能不能在大力面前做个谦虚的小学生？哪怕你将来上了人大，上了北大，北大法学研究生博士毕业，到了律所里面，见到一个江苏大学毕业的或者苏罗大学毕业的，你会不会觉得说你这个律师，你学校还不如我，能够凭什么给你拎包啊？
  标准化：能否在前辈面前做个谦虚的小学生，即使北大法学博士毕业也要从基础做起？
  预期工具：employment_summary, school_lookup；缺槽：provinces；质量：A

### school_major_profile

- 问法：某一年,河南省某学校在另外一个省分招生出现一个非常有意思的现象。就是它普通办学和中外合作办学分数倒挂。什么意思呢?就是这个学校的中外合作办学分数高,但是它普通办学分数低。就是我考了更高的分上同一个学校,但我只能上中外合作办学,我要教更多的学费。然后更低分的同学。
  标准化：为什么会出现同一所学校中外合作办学分数高于普通专业分数的现象？
  预期工具：school_major_profile, admission_history, data_gap_detection；缺槽：学校名称, 另一个省名称, 具体年份, 招生人数, 最低/最高分数；质量：B
- 问法：比如说你在想报法学，但有的学校法学下面可以接财经类和汉语言，也就是说法学下班入不了的话，财经类和汉语言能给你接住，这两个也是你能接受的。但有的学校专业除了法学以外，下班要么是外语专业，要么是旅游管理专业，要么是社会学专业。那多大的意思吗？对，那你肯定要报能接得住你的学校，而不是要报接不住你的学校。
  标准化：不同学校法学类专业的备选方向不同，应如何根据备选专业选择学校？
  预期工具：school_major_profile, major_lookup；缺槽：score, rank, province, target_schools；质量：B
- 问法：大家好，我听说张雪峰老师一年一度的高考志愿又到了。我知道这两天大家都陆续拿到分数了，开始为填志愿的事情烦恼着，所以马上就会给各位家长和考生送上我最精华一期2021年志愿填报的核心内容。每年都有很多同学跟我说，除那些专业又好、学校又好、排名又靠前的大学外，我们都知道，但是录取的分数太高了，能不能给大家推荐一些，分数稍微低一点的
  标准化：有没有录取分数低一点，但专业又好、就业又好的大学推荐？
  预期工具：school_major_profile, major_profile, employment_summary；缺槽：省份, 分数, 位次, 学校, 专业；质量：B
- 问法：家里有高三理科生，平时考试成绩在550分左右。之前想让他学医，但前几天突然查出有色弱，规划就打乱了。很多专业受限，想让张老师推荐一些院校和专业，希望在省内、合肥或者一线城市工作，能留在当地的。
  标准化：家有高三理科生，成绩550左右，有色弱，想请老师推荐不受限的院校和专业，地域偏好在省内或一线城市？
  预期工具：school_lookup, major_lookup, score_to_rank, specialty_group_lookup；缺槽：province, target_provinces；质量：B

### comparison_query

- 问法：你要问985好一点，我们不如问一下，清华大学好一点还是别的学校好一点，我就不具体力量了。
  标准化：清华大学和其他985高校哪个更好？
  预期工具：school_lookup, school_major_profile；缺槽：specific_school；质量：A
- 问法：就是以你现在的分数能报的那个院校和层次，以及它先用能不能五加三或者怎么样的，就是你报医学可能会对你未来更没保障。
  标准化：以现在的分数能报什么院校和层次？报医学是否对未来更没保障？
  预期工具：comparison_query, school_lookup；缺槽：score, provinces, schools；质量：B
- 问法：然后他自己想了一下，他想学法学，我呢也想了一下，我觉得好像医学更好一些。现在我们两个想问问你，两个专业的话哪一个将来就业会好一些。家长喜欢医学，然后孩子要报什么？孩子想报法学，因为他觉得自己动手能力不太强。
  标准化：法学和医学哪个专业将来就业更好？
  预期工具：comparison_query, major_lookup；缺槽：省份, 分数；质量：B
- 问法：我想问一下，就是说是上这个本科、上这个中科里大学好，还是上这个专业里院校好？
  标准化：高考分数有限，上本科大学还是专科院校更好？
  预期工具：comparison_query；缺槽：score, province, intended_major；质量：B
- 问法：我们充一充和稳稳该怎么报？
  标准化：冲一冲和稳稳该怎么报？
  预期工具：rank_to_school_match, school_lookup；缺槽：省份, 分数, 位次；质量：B

### transfer_policy_lookup

- 问法：充志愿和稳专业该怎么报
  标准化：充志愿和稳专业应该怎么报？
  预期工具：major_lookup, school_lookup；缺槽：省份, 分数, 位次, 选科；质量：B
- 问法：我们下面讲一张比较隔行的叫保一保该怎么报
  标准化：保一保志愿该怎么填报？
  预期工具：rank_to_school_match, school_lookup, transfer_policy_lookup；缺槽：province, subject_category, batch_type, score, rank；质量：B

### rank_to_major_match

- 问法：他现在有550分，我就想问能报什么样的专业。
  标准化：高考550分能报什么专业？
  预期工具：major_lookup, score_to_rank, rank_to_major_match；缺槽：无；质量：B
- 问法：学业中期可能会相对比较长。第五个问题要不要选化学？第六个问题要不要选物理？你这老师，我物理也不好，化学也不好，数学还不错，那你的专业就出来了什么呢？数学、统计、计算也不错。这三个专业上大学没有物理，没有化学，没有生物。
  标准化：物理化学不好但数学好的考生适合选什么专业？
  预期工具：rank_to_major_match, major_lookup, subject_requirement_lookup；缺槽：省份, 分数, 位次, 数学能力, 物理能力, 化学能力；质量：B

### major_market_reference

- 问法：他刚才问说张老师我们家还在报了一个专业叫电子封装技术，研究生能不能转通信，因为电子封装技术是偏电子并不是偏通信，他在问的是张老师我报一个电子类的本科专业，然后考研能不能转通信，他问的是这个意思，这个家长分得非常专，但是你为什么不直接报一个通信呢？
  标准化：电子封装技术专业本科毕业能否考研转向通信专业？
  预期工具：major_market_reference, subject_requirement_lookup；缺槽：无；质量：A

### score_to_rank

- 问法：我真想问一下，我有一个妹妹，她现在是在普通高中，她选的是物理、化学还有政治。她考520分，520左右是吧？
  标准化：我妹妹高考成绩520分，选科是物理、化学、政治，能报考哪些学校？
  预期工具：score_to_rank, school_lookup, major_lookup；缺槽：province, rank；质量：B

### subject_requirement_lookup

- 问法：可以可以，我在跟他讲，他学医不行，他学医不行的英语60分，他英语60分，他化学学生物在好考研不考英语吗？
  标准化：英语60分能学医吗？化学和生物方向考研是否不考英语？
  预期工具：major_lookup, subject_requirement_lookup；缺槽：无；质量：A
- 问法：好,那要带物理吗?不可以带物理。要带物理的话,你力学好还是电学好?多还行。多还行是吧?那你基本上就是一个所谓的经典公课开局,就是借段积数学土地也能接受是吧?对,那你这部经典的公课开局吗?借段积数学土地加中电的公课?
  标准化：物理学科组合如何选择?选择物理的话力学和电磁学哪个更好？
  预期工具：subject_requirement_lookup；缺槽：学科组合偏好, 物理成绩偏好；质量：B

### civil_service_role_search

- 问法：因为我之前也给大家讲过，您问我这个专业能不能考公务员，都可以考。没有问题，所有的专业都可以考公务员。
  标准化：所有专业都可以考公务员吗？
  预期工具：civil_service_role_search；缺槽：具体省份, 具体岗位；质量：D

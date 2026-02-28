-- Unobfuscated label candidates for targeted confirmation runs
select
  source_type,
  name,
  confidence,
  count(*) as occurrences,
  count(distinct source_file) as distinct_files,
  min(case when line > 0 then line end) as first_line,
  max(case when line > 0 then line end) as last_line
from name_candidates
group by source_type, name, confidence
order by occurrences desc, distinct_files desc, source_type asc, name asc
limit 500;

-- Evidence rollup hotspots for accepted/triage review
select
  class_name,
  evidence_source,
  evidence_detail,
  occurrence_count,
  distinct_files,
  first_line,
  last_line,
  sample_source_file
from proto_evidence_rollup
order by occurrence_count desc, distinct_files desc, class_name asc
limit 200;

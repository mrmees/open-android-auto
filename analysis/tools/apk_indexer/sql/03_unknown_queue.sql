-- Unknown queue sorted for manual triage
select
  class_name,
  reason,
  evidence_count,
  notes
from proto_unknowns
order by evidence_count desc, class_name asc;

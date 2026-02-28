-- Field-oriented view of accepted proto catalog entries
select
  class_name,
  apk_version,
  field_count,
  confidence,
  case when length(descriptor) > 0 then 1 else 0 end as has_descriptor
from proto_catalog
order by field_count desc, class_name asc;

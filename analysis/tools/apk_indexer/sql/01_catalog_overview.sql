-- Catalog totals by confidence tier
select confidence, count(*) as n
from proto_catalog
group by confidence
order by n desc, confidence asc;

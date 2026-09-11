# Included team charter snapshots

Each team directory contains its `CHARTER.md` and `OBJECTIVES.md` at the
revision recorded in [repository-snapshot.json](../../repository-snapshot.json).
The copies let the planning repository rebuild its complete reader without
cloning the eleven component repositories or fetching files during a build.
Each included team README is a planning navigation aid that links to the
upstream repository structure; the charter and objective files remain exact.

The original team repositories remain authoritative. These snapshots do not
assign members, replace team-owned documents or add a new engineering team.
The [team manifest](../team-manifest.json) records the display role and supplied
starter-code status used by the reader at the same snapshot.

To refresh a team's snapshot, select and verify the intended source revision,
copy both documents exactly from that revision, and update its entry in
`repository-snapshot.json`. If refreshing the full snapshot, verify visibility,
commit counts and the check timestamp as well. Update the manifest if the
team's role or supplied-code status has changed. Rebuild and review the output
with the corresponding source changes.

Relative links inside imported documents are rewritten to the recorded GitHub
revision by the reader builder. Keep the source copies exact so their hashes
can be compared with the upstream files.

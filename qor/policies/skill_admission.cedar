// Skill admission policy for QorLogic governance.
// A skill may be invoked only if it is registered and has frontmatter.

permit (
  principal,
  action == Action::"invoke",
  resource
) when { resource.registered == true && resource.has_frontmatter == true };

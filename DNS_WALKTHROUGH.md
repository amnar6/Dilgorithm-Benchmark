# DNS Walkthrough: Resolving Web Addresses & CNAME Aliasing

## 1. The Journey of a Web Request
When someone types `amnaa-r.flyrank.ai` into their web browser, computers must convert that human-readable name into a numerical IP address to locate the hosting server. This resolution process happens in four distinct steps:

1. **Recursive Resolver:** The user's browser sends a query to the Recursive Resolver (typically managed by the ISP or a public provider like 1.1.1.1). The resolver checks its cache; if uncached, it initiates a global lookup chain.
2. **Root & TLD Nameservers:** The resolver queries the internet Root Nameserver, which directs it to the Top-Level Domain (TLD) nameserver responsible for `.ai`. The `.ai` TLD nameserver identifies the authoritative nameserver handling the `flyrank.ai` zone.
3. **Authoritative Nameserver:** The resolver queries the Authoritative Nameserver for `flyrank.ai`. This server inspects its DNS records and finds a CNAME record mapping `amnaa-r.flyrank.ai` to `amnaa-r.netlify.app`.
4. **Final IP Response & Handshake:** The resolver follows the alias, queries Netlify's DNS infrastructure to get the active edge server IP address, and returns that IP to the browser. The browser then establishes an encrypted HTTPS handshake with Netlify and renders the site.

---

## 2. What is a CNAME Record?
A **CNAME (Canonical Name)** record is a DNS record that maps an alias domain directly to another domain name rather than pointing to a fixed numerical IP address.

* **Alias (Host Name):** `amnaa-r.flyrank.ai`
* **Target (Canonical Name):** `amnaa-r.netlify.app`

### Why CNAME Aliasing is Used Here
Modern cloud platform edge networks (like Netlify) distribute site content across thousands of dynamic servers globally. Their physical IP addresses change frequently for load balancing and DDoS mitigation. Using a CNAME record allows FlyRank Ops to point `amnaa-r.flyrank.ai` at Netlify's domain alias, letting Netlify manage IP routing changes in the background without requiring manual DNS updates.

---

## 3. Subdomain Setup Checklist (Capstone Phase)
When the `amnaa-r.flyrank.ai` subdomain is provisioned at the end of the track:

1. **Ops Provisioning:** FlyRank Ops configures the CNAME record in the domain registrar mapping `amnaa-r.flyrank.ai` to `amnaa-r.netlify.app`.
2. **Host Binding:** Log into Netlify $\rightarrow$ Site Configuration $\rightarrow$ Domain Management $\rightarrow$ Add custom domain (`amnaa-r.flyrank.ai`).
3. **SSL/TLS Provisioning:** Netlify detects the CNAME alignment and automatically requests an SSL certificate via Let's Encrypt.
4. **Verification:** Open `https://amnaa-r.flyrank.ai` in a logged-out private browser window and verify HTTPS padlock activation.
import Link from "next/link";
export default function SiteFooter(){
 return <footer className="hc-unified-footer"><div className="hc-footer-top"><div><strong>HERSHEY SUPPLY CHAIN AI</strong><p>Independent academic study · Praveen Rathee</p></div><nav aria-label="Footer navigation"><Link href="/">Home</Link><Link href="/supply-chain">Supply Chain</Link><Link href="/evidence-brain">Evidence</Link><Link href="/cost-model">Cost Model</Link><Link href="/sources">Sources</Link><Link href="/methodology">How It Works</Link></nav><a href="#top">Back to top ↑</a></div><p className="hc-footer-note">Public-source research and benchmark estimates. Not affiliated with, endorsed by or sponsored by The Hershey Company. Product names and trademarks belong to their respective owners.</p></footer>
}

const API_BASE = "http://127.0.0.1:5000/api";

let currentAnalysis = null;

function scrollToReport(){document.getElementById("report").scrollIntoView({behavior:"smooth"});}
function scrollToMap(){document.getElementById("map-section").scrollIntoView({behavior:"smooth"});}

const imageInput=document.getElementById("imageInput");
const previewImage=document.getElementById("previewImage");
const uploadContent=document.getElementById("uploadContent");
const analysisEmpty=document.getElementById("analysisEmpty");
const analysisLoading=document.getElementById("analysisLoading");
const analysisResult=document.getElementById("analysisResult");

imageInput.addEventListener("change", async function(){
  const file=this.files[0];
  if(!file)return;
  if(!file.type.startsWith("image/")){alert("Please select an image.");return;}
  const reader=new FileReader();
  reader.onload=e=>{previewImage.src=e.target.result;previewImage.style.display="block";uploadContent.style.display="none";};
  reader.readAsDataURL(file);
  await analyzeImage(file);
});

async function analyzeImage(file){
  analysisEmpty.classList.add("hidden");
  analysisResult.classList.add("hidden");
  analysisLoading.classList.remove("hidden");
  const form=new FormData();
  form.append("image",file);
  try{
    const response=await fetch(`${API_BASE}/analyze`,{method:"POST",body:form});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||"Analysis failed");
    currentAnalysis=data;
    document.getElementById("detectedProblem").textContent=data.problem_type;
    document.getElementById("confidence").textContent=`${data.confidence}%`;
    document.getElementById("severity").textContent=data.severity;
    document.getElementById("priorityScore").textContent=data.priority_score;
    document.getElementById("priorityFill").style.width=`${data.priority_score}%`;
    getLocation();
    analysisLoading.classList.add("hidden");
    analysisResult.classList.remove("hidden");
  }catch(error){
    analysisLoading.classList.add("hidden");
    analysisEmpty.classList.remove("hidden");
    alert("Backend connection failed. Start Flask with: python app.py");
    console.error(error);
  }
}

function getLocation(){
  const el=document.getElementById("location");
  if(!navigator.geolocation){el.textContent="GPS unavailable";return;}
  el.textContent="Detecting...";
  navigator.geolocation.getCurrentPosition(
    p=>{currentAnalysis.latitude=p.coords.latitude;currentAnalysis.longitude=p.coords.longitude;el.textContent=`${p.coords.latitude.toFixed(5)}, ${p.coords.longitude.toFixed(5)}`;},
    ()=>{el.textContent="Location unavailable";}
  );
}

async function submitReport(){
  if(!currentAnalysis){alert("Analyse an image first.");return;}
  const payload={
    problem_type:currentAnalysis.problem_type,
    severity:currentAnalysis.severity,
    priority_score:currentAnalysis.priority_score,
    latitude:currentAnalysis.latitude??null,
    longitude:currentAnalysis.longitude??null,
    image:currentAnalysis.image??null
  };
  try{
    const response=await fetch(`${API_BASE}/reports`,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(payload)
    });
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||"Submission failed");
    alert(`Report submitted successfully!\n\nReport ID: ND-${data.report_id}`);
    await loadReports();
  }catch(error){
    alert("Could not submit report. Make sure the backend is running.");
    console.error(error);
  }
}

async function loadReports(){
  try{
    const response=await fetch(`${API_BASE}/reports`);
    const data=await response.json();
    if(!response.ok)return;
    const rows=document.getElementById("reportRows");
    rows.innerHTML="";
    data.reports.forEach(r=>{
      const row=document.createElement("div");
      row.className="table-row";
      const priorityClass=r.priority_score>=80?"priority-high":"priority-medium";
      const statusClass=r.status==="Resolved"?"resolved":(r.status==="Assigned"?"assigned":"pending");
      row.innerHTML=`<span>📝 ${escapeHtml(r.problem_type)}</span><span>${r.latitude&&r.longitude?`${Number(r.latitude).toFixed(4)}, ${Number(r.longitude).toFixed(4)}`:"Location unavailable"}</span><b class="${priorityClass}">${r.priority_score}</b><span class="status ${statusClass}">${escapeHtml(r.status)}</span>`;
      rows.appendChild(row);
    });
    document.getElementById("problemCount").textContent=(1248+data.count).toLocaleString();
  }catch(e){console.log("Reports unavailable:",e);}
}

function escapeHtml(value){
  return String(value).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
}

const map=L.map("map").setView([28.6139,77.2090],12);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"&copy; OpenStreetMap contributors"}).addTo(map);

const civicProblems=[
  {lat:28.6139,lng:77.2090,title:"Large Pothole",type:"🕳️",priority:92},
  {lat:28.6280,lng:77.2150,title:"Broken Footpath",type:"🚶",priority:87},
  {lat:28.6000,lng:77.1900,title:"Garbage Accumulation",type:"🗑️",priority:67},
  {lat:28.6400,lng:77.2300,title:"Damaged Streetlight",type:"💡",priority:61},
  {lat:28.5900,lng:77.2200,title:"Road Damage",type:"🚧",priority:78}
];

civicProblems.forEach(p=>{
  const marker=L.marker([p.lat,p.lng]).addTo(map);
  marker.bindPopup(`<strong>${p.type} ${p.title}</strong><br><br>Civic Priority: <strong>${p.priority}/100</strong><br><br><button onclick="viewProblem('${p.title.replace(/'/g,"\\'")}')" style="background:#e45b24;color:white;border:none;padding:7px 12px;border-radius:6px;cursor:pointer">View Report</button>`);
});

function viewProblem(title){alert(`NagarDrishti Report\n\nProblem: ${title}\nStatus: Pending inspection`);}

const uploadBox=document.getElementById("uploadBox");
uploadBox.addEventListener("dragover",e=>{e.preventDefault();uploadBox.style.borderColor="#e45b24";});
uploadBox.addEventListener("dragleave",()=>uploadBox.style.borderColor="#d7dbe0");
uploadBox.addEventListener("drop",e=>{
  e.preventDefault();uploadBox.style.borderColor="#d7dbe0";
  const file=e.dataTransfer.files[0];
  if(file&&file.type.startsWith("image/")){
    const dt=new DataTransfer();dt.items.add(file);imageInput.files=dt.files;
    imageInput.dispatchEvent(new Event("change"));
  }
});

loadReports();
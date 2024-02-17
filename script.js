var apiResponse=[];
var currentPage=1;
var itemsPerPage=10;

function loadData(){
    fetch('https://boiling-oasis-31121-583e8833575b.herokuapp.com/proxies')
    .then(response=>response.json())
    .then(data=>{
        apiResponse=data;
        updateTable();
        populateDropdowns();
    })
    .catch(error=>console.error('Error loading data:',error))
}

function updateTable() {
    const tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = '';
    const startIndex = (currentPage - 1) * itemsPerPage;

    const countryFilter = document.getElementById('countryDropdown').querySelector('.search-input').value.toUpperCase();
    const asnFilter = document.getElementById('asnDropdown').querySelector('.search-input').value.toUpperCase();
    const protocolFilters = Array.from(document.querySelectorAll('.toggle-button.active')).map(button => button.textContent.toUpperCase());

    const filteredProxies = apiResponse.filter(proxy => {
        const countryMatch = countryFilter === '' || proxy.country.toUpperCase().includes(countryFilter);
        const asnMatch = asnFilter === '' || (proxy.asn && proxy.asn.toString().toUpperCase().includes(asnFilter));
        const protocolMatch = protocolFilters.includes(proxy.protocol.toUpperCase());
        return countryMatch && asnMatch && protocolMatch;
    });

    filteredProxies.slice(startIndex, startIndex + itemsPerPage).forEach(proxy => {
        const row = tableBody.insertRow();
        ['ip', 'port', 'country', 'protocol', 'asn', 'city'].forEach(field => {
            const cell = row.insertCell();
            cell.textContent = proxy[field] ? proxy[field] : '';
        });
    });

    const totalProxiesCountElement = document.getElementById('totalProxiesCount');
    totalProxiesCountElement.textContent = `Total Proxies: ${apiResponse.length} | Filtered Proxies: ${filteredProxies.length}`;

    updatePagination(filteredProxies.length);
}

function updatePagination(){
    const totalPages=Math.ceil(apiResponse.length/itemsPerPage);
    document.getElementById('totalPages').textContent=totalPages;
    document.getElementById('currentPage').textContent=currentPage;
}

function filterDropdown(containerId,input){
    const filterValue=input.value.toUpperCase();
    const dropdownContent=document.getElementById(containerId);
    const buttons=dropdownContent.getElementsByTagName('button');
    for(let i=0;i<buttons.length;i++){
        const button=buttons[i];
        const textValue=button.textContent||button.innerText;
        if(textValue.toUpperCase().indexOf(filterValue)>-1){
            button.style.display=''
        }else{
            button.style.display='none'
        }
    }
}

function filterProtocol(protocol){
    const protocolButton=document.getElementById(protocol.toLowerCase()+'Toggle');
    protocolButton.classList.toggle('active');
    updateTable();
}

function exportData(format) {
    let exportContent = '';
    const fieldsToExport = Array.from(document.querySelectorAll('input[name="exportField"]:checked'));
    const proxiesToShow = apiResponse.filter(proxy => {
        const countryFilter = document.getElementById('countryDropdown').querySelector('.search-input').value.toUpperCase();
        const asnFilter = document.getElementById('asnDropdown').querySelector('.search-input').value.toUpperCase();
        const protocolFilters = Array.from(document.querySelectorAll('.toggle-button.active')).map(button => button.textContent.toUpperCase());
        const countryMatch = countryFilter === '' || proxy.country.toUpperCase().includes(countryFilter);
        const asnMatch = asnFilter === '' || (proxy.asn && proxy.asn.toString().toUpperCase().includes(asnFilter));
        const protocolMatch = protocolFilters.length === 0 || protocolFilters.includes(proxy.protocol.toUpperCase());
        return countryMatch && asnMatch && protocolMatch;
    });

    proxiesToShow.forEach(proxy => {
        let rowData = fieldsToExport.map(field => {
            return proxy[field.value] != null ? proxy[field.value].toString() : '';
        }).join(':');

        exportContent += rowData + '\n';
    });

    const filename = `proxies.${format}`;
    const blob = new Blob([exportContent], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function nextPage(){
    const totalPages=Math.ceil(apiResponse.length/itemsPerPage);
    if(currentPage<totalPages){
        currentPage++;
        updateTable();
    }
}

function changeItemsPerPage(value){
    itemsPerPage=parseInt(value);
    currentPage=1;
    updateTable();
}

function populateDropdowns(){
    const countries=new Set();
    const asns=new Set();
    apiResponse.forEach(proxy=>{
        countries.add(proxy.country);
        asns.add(proxy.asn);
    });
    const countryDropdownContent=document.getElementById('countryDropdownContent');
    countries.forEach(country=>{
        const button=document.createElement('button');
        button.textContent=country;
        button.onclick=()=>filterByCountry(country);
        countryDropdownContent.appendChild(button);
    });
    const asnDropdownContent=document.getElementById('asnDropdownContent');
    asns.forEach(asn=>{
        const button=document.createElement('button');
        button.textContent=asn;
        button.onclick=()=>filterByASN(asn);
        asnDropdownContent.appendChild(button);
    });
}

function filterByCountry(country) {
    const countryInput = document.getElementById('countryDropdown').querySelector('.search-input');
    countryInput.value = country;
    updateTable();
    updateAsnDropdown(country);
}

function filterByASN(asn) {
    const asnInput = document.getElementById('asnDropdown').querySelector('.search-input');
    asnInput.value = asn;
    updateTable();
}

function updateAsnDropdown(country) {
    const asnDropdownContent = document.getElementById('asnDropdownContent');
    asnDropdownContent.innerHTML = '';
    const uniqueAsns = new Set(apiResponse.filter(proxy => !country || proxy.country === country).map(proxy => proxy.asn));
    uniqueAsns.forEach(asn => {
        const button = document.createElement('button');
        button.textContent = asn;
        button.onclick = () => filterByASN(asn);
        asnDropdownContent.appendChild(button);
    });
}

function clearFilter(dropdownId){
    const input=document.getElementById(dropdownId).querySelector('.search-input');
    input.value='';
    filterDropdown(dropdownId+'Content',input);
    updateTable();
}

window.onload=loadData;

if [ $# -eq 0 ]; then
    nw=($(docker network ls | awk 'NR>=2 {printf "%s ",$2}'))
else
    nw=$@
fi

echo ${nw[@]}
for network in ${nw[@]};do

    docker network ls | grep $network 1>/dev/null 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "\nNetwork $network not found!"
        exit 1
    fi

    ids=$(docker network inspect $network | grep -E "^\s+\".{64}\"" | awk -F\" '{printf "%s ",substr($2,0,12)}')
    echo -e "\nContainers in network $network:"
    for id in ${ids[@]}; do
        name=$(docker ps -a | grep $id | awk '{print $NF}')
        echo -e "\t$id: $name"
    done
    shift
done
